defmodule Peep.Buckets.CustomTuple do
  @moduledoc """
  A helper module for writing modules that implement the `Peep.Buckets` behavior
  with custom bucket boundaries, optimized to use a tuple of boundaries.

  This module expects the boundaries to be provided as an ordered tuple (or list)
  in the `:buckets` option. It can receive a literal (list or tuple) or a
  module attribute (e.g., `@my_buckets`). It generates functions that operate directly
  on the final tuple at runtime, including a binary search for `bucket_for/2`.

  Usage:
    defmodule MyBuckets do
      # Boundaries MUST be ordered if provided as a tuple literal or attribute
      @boundaries {0.1, 0.5, 1.0, 5.0}
      use Peep.Buckets.CustomTuple, buckets: @boundaries

      # Or: use Peep.Buckets.CustomTuple, buckets: [0.1, 5.0, 1.0] # Will be sorted
      # Or: use Peep.Buckets.CustomTuple, buckets: {0.1, 0.5, 1.0, 5.0} # Literal
    end
  """

  defmacro __using__(opts) do
    # Get the expression passed to :buckets
    buckets_expr = Keyword.fetch!(opts, :buckets)
    # Get the environment from where the macro was called
    env = __CALLER__

    # 1. Resolve the :buckets expression to get a RAW LIST of elements
    raw_elements_list =
      case buckets_expr do
        # Case 1: The expression is a module attribute, like `@my_var`
        {:@, _meta, [{attr_name, _attr_meta, nil}]} ->
          case Module.get_attribute(env.module, attr_name) do
            nil ->
              raise ArgumentError,
                    "Module attribute @#{attr_name} not found or is nil in module #{inspect(env.module)} when resolving :buckets"

            value when is_list(value) ->
              value # Attribute was a list

            value when is_tuple(value) ->
              Tuple.to_list(value) # Attribute was a tuple, convert to list

            value ->
              raise ArgumentError,
                    "Module attribute @#{attr_name} resolved to #{inspect(value)}, but expected a list or tuple for :buckets"
          end

        # Case 2: The expression is a list literal `[...]`
        # The AST of a list literal *is* the list itself
        list when is_list(list) ->
          list

        # Case 3: The expression is a tuple literal `{...}`
        # The AST is {: {}, meta, elements_list}
        {:{}, _meta, elements_list} when is_list(elements_list) ->
          elements_list # We extract the list of elements from the AST

        # Case 4: Unknown expression
        other ->
          raise ArgumentError,
                "Could not resolve :buckets option. Expected a literal list/tuple or @attribute, got: #{Macro.to_string(other)}"
      end

    # 2. Validate that the list of elements contains only numbers
    unless Enum.all?(raw_elements_list, &is_number/1) do
      raise ArgumentError,
            "Expected :buckets (resolved from #{Macro.to_string(buckets_expr)}) to contain only numbers, got: #{inspect(raw_elements_list)}"
    end

    # 3. Sort the list to ensure correct order for binary search
    #    This handles input lists and ensures that even tuples (which should be ordered)
    #    are treated correctly if they weren't.
    sorted_list = Enum.sort(raw_elements_list)

    # Optional: Check if the original input (if tuple) was already sorted
    # if match?({:{}, _, _}, buckets_expr) and raw_elements_list != sorted_list do
    #   IO.warn("The tuple literal provided for :buckets was not sorted. Sorting automatically.", Macro.Env.location(env))
    # end

    # 4. Convert the final sorted list into the tuple that will be used at runtime
    boundaries_tuple = List.to_tuple(sorted_list)
    number_of_buckets = tuple_size(boundaries_tuple)

    # 5. Pre-compute upper bound strings
    upper_bound_strings =
      sorted_list # Use the sorted list directly, avoids Tuple.to_list
      |> Enum.map(&boundary_to_string/1)
      |> Kernel.++(["+Inf"])
      |> List.to_tuple()

    # 6. Generate the target module code
    quote do
      @behaviour Peep.Buckets

      # Store precomputed data as module attributes
      # !!! FIX HERE: Use Macro.escape/1 for the tuples !!!
      @number_of_buckets unquote(number_of_buckets) # Simple value, OK
      @boundaries_tuple unquote(Macro.escape(boundaries_tuple)) # Escape the boundaries tuple
      @upper_bound_strings unquote(Macro.escape(upper_bound_strings)) # Escape the strings tuple

      @impl true
      def config(_), do: %{}

      @impl true
      def number_of_buckets(_), do: @number_of_buckets

      @impl true
      def upper_bound(bucket_index, _)
          when is_integer(bucket_index) and bucket_index >= 0 and
                 bucket_index < tuple_size(@upper_bound_strings) do
        # Access the @upper_bound_strings attribute, which is now correctly defined
        elem(@upper_bound_strings, bucket_index)
      end

      @impl true
      def bucket_for(value, _) when is_number(value) do
        # Call the generated helper function, which will use @boundaries_tuple
        find_bucket_index(value, @boundaries_tuple, @number_of_buckets)
      end

      def bucket_for(value, _) do
        raise ArgumentError, "bucket_for/2 requires a number, got: #{inspect(value)}"
      end

      # --- Generated Helper Functions (private) ---
      @spec find_bucket_index(number(), tuple(), non_neg_integer()) :: non_neg_integer()
      defp find_bucket_index(value, boundaries_tuple, num_buckets) do
        # Special case: no boundaries defined
        if num_buckets == 0,
           do: 0,
           else: do_binary_search(value, boundaries_tuple, 0, num_buckets - 1, num_buckets)
      end

      # Binary search function optimized to find the bucket index.
      # Finds the smallest index `i` such that `value < elem(boundaries_tuple, i)`.
      # Returns `num_buckets_total` if `value` is greater than or equal to the last boundary.
      defp do_binary_search(value, tuple, low, high, num_buckets_total)

      # Base case of the recursion: low crossed high.
      # 'low' now represents the index of the first bucket whose lower bound
      # is greater than or equal to 'value'. This is the bucket index we want.
      defp do_binary_search(_value, _tuple, low, high, _num_buckets_total) when low > high, do: low

      # Recursive step of the binary search
      defp do_binary_search(value, tuple, low, high, num_buckets_total) do
        mid = div(low + high, 2)
        mid_val = elem(tuple, mid)

        if value < mid_val do
          # The value is less than the middle boundary. The correct index is in the left half (including mid).
          # Search in the interval [low, mid - 1].
          do_binary_search(value, tuple, low, mid - 1, num_buckets_total)
        else
          # The value is greater than or equal to the middle boundary. The correct index is in the right half (excluding mid).
          # Search in the interval [mid + 1, high].
          do_binary_search(value, tuple, mid + 1, high, num_buckets_total)
        end
      end
    end
  end

  # ===========================================
  # Compile-Time Helpers (Used by the Macro)
  # ===========================================

  # Converts a numeric boundary to a formatted string
  @spec boundary_to_string(number()) :: String.t()
  defp boundary_to_string(number) when is_integer(number) do
    # Ensure float format (e.g., 10 -> "10.0") for consistency
    :io_lib.format("~.1f", [number * 1.0]) |> List.to_string()
  end

  defp boundary_to_string(number) when is_float(number) do
    # Converting float to string might need precision handling if required
    to_string(number) # Simple conversion
  end
end
