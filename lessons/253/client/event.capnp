@0x984f828f18945882;

struct Quote {
  # The event type.
  ev @0 :Text;

  # The ticker symbol for the given stock.
  sym @1 :Text;

  # The bid exchange ID.
  bx @2 :Int16;

  # The bid price.
  bp @3 :Float64;

  # The bid size.
  bs @4 :Int16;

  # The ask exchange ID.
  ax @5 :Int16;

  # The ask price.
  ap @6 :Float64;

  # The ask size. 
  as @7 :Int64;

  # The condition.
  c @8 :Int16;

  # The indicators.
  i @9 :List(Int32);

  # The SIP timestamp in Unix MS.
  t @10 :Int64;

  # The sequence number represents the sequence in which quote events happened.
  q @11 :Int64;

  # The tape. (1 = NYSE, 2 = AMEX, 3 = Nasdaq).
  z @12 :Int8;

  # A timestamp is used to measure latency.
  tb @13 :Int64;
}
