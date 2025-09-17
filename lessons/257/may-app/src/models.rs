use yarte::Serialize;

#[derive(Serialize)]
pub(crate) struct Ticker {
    pub(crate) symbol: &'static str,
    pub(crate) bid_price: &'static str,
    pub(crate) bid_qty: &'static str,
    pub(crate) ask_price: &'static str,
    pub(crate) ask_qty: &'static str,
}
