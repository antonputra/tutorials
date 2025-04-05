defmodule Peep.Buckets.CustomTuple do
  @moduledoc """
  A helper module for writing modules that implement the `Peep.Buckets` behavior
  with custom bucket boundaries using only tuples.

  This module expects the boundaries to be provided as an ordered tuple
  in the `:buckets` option. It generates functions that operate directly
  on the tuple at runtime, including a binary search for `bucket_for/2`.

  Usage:
    defmodule MyBuckets do
      @boundaries {0.1, 0.5, 1.0, 5.0}  # Must be sorted
      use Peep.Buckets.CustomTuple, buckets: @boundaries
    end
  """

  defmacro __using__(opts) do
    buckets_expr = Keyword.fetch!(opts, :buckets)
    env = __CALLER__

    {raw_elements_list, boundaries_tuple} =
      case buckets_expr do
        {:@, _, [{attr_name, _, nil}]} ->
          case Module.get_attribute(env.module, attr_name) do
            nil ->
              raise ArgumentError, "Attribute @#{attr_name} not found in #{env.module}"
            val when is_tuple(val) ->
              list = Tuple.to_list(val)
              unless is_sorted(list) do
                raise ArgumentError, "Attribute @#{attr_name} must be a sorted tuple"
              end
              {list, val}
            other ->
              raise ArgumentError, "@#{attr_name} must be a tuple, got: #{inspect(other)}"
          end

        {:{}, _, elements} when is_list(elements) ->
          unless is_sorted(elements) do
            raise ArgumentError, "Tuple literal must be sorted"
          end
          {elements, List.to_tuple(elements)}

        other ->
          raise ArgumentError, "Invalid buckets: must be a tuple. Got: #{Macro.to_string(other)}"
      end

    unless Enum.all?(raw_elements_list, &is_number/1) do
      raise ArgumentError, "Buckets must contain numbers. Got: #{inspect(raw_elements_list)}"
    end

    number_of_buckets = tuple_size(boundaries_tuple)

    upper_bound_strings =
      raw_elements_list
      |> Enum.map(&boundary_to_string/1)
      |> Kernel.++(["+Inf"])
      |> List.to_tuple()

    quote do
      @behaviour Peep.Buckets

      @number_of_buckets unquote(number_of_buckets)
      @boundaries_tuple unquote(Macro.escape(boundaries_tuple))
      @upper_bound_strings unquote(Macro.escape(upper_bound_strings))

      @impl true
      def config(_), do: %{}

      @impl true
      def number_of_buckets(_), do: @number_of_buckets

      @impl true
      def upper_bound(bucket_index, _) do
        elem(@upper_bound_strings, bucket_index)
      end

      @impl true
      def bucket_for(value, _) when is_number(value) do
        find_bucket_index(value, @boundaries_tuple, @number_of_buckets)
      end

      def bucket_for(value, _) do
        raise ArgumentError, "bucket_for/2 requires a number, got: #{inspect(value)}"
      end

      defp find_bucket_index(value, boundaries, num_buckets) do
        if num_buckets == 0 do
          0
        else
          do_binary_search(value, boundaries, 0, num_buckets - 1, num_buckets)
        end
      end

      defp do_binary_search(_, _, low, high, _) when low > high, do: low

      defp do_binary_search(value, tuple, low, high, total) do
        mid = div(low + high, 2)
        mid_val = elem(tuple, mid)

        if value < mid_val do
          do_binary_search(value, tuple, low, mid - 1, total)
        else
          do_binary_search(value, tuple, mid + 1, high, total)
        end
      end
    end
  end

  defp is_sorted([]), do: true
  defp is_sorted([_]), do: true
  defp is_sorted([a, b | rest]) when a <= b, do: is_sorted([b | rest])
  defp is_sorted(_), do: false

  defp boundary_to_string(n) when is_integer(n), do: "#{n}.0"
  defp boundary_to_string(n) when is_float(n), do: to_string(n)
end
