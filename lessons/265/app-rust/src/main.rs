use actix_web::{App, HttpServer, Responder, web};
use serde::Serialize;

#[derive(Serialize)]
struct Ticker {
    symbol: &'static str,
    #[serde(rename = "bidPrice")]
    bid_price: &'static str,
    #[serde(rename = "bidQty")]
    bid_qty: &'static str,
    #[serde(rename = "askPrice")]
    ask_price: &'static str,
    #[serde(rename = "askQty")]
    ask_qty: &'static str,
}

async fn get_tickers() -> impl Responder {
    // Preallocate vector with exact capacity same as C++
    let mut tickers = Vec::with_capacity(2);
    tickers.push(Ticker {
        symbol: "LTCBTC",
        bid_price: "4.00000000",
        bid_qty: "431.00000000",
        ask_price: "4.00000200",
        ask_qty: "9.00000000",
    });
    tickers.push(Ticker {
        symbol: "ETHBTC",
        bid_price: "0.07946700",
        bid_qty: "49.00000000",
        ask_price: "100000.00000000",
        ask_qty: "1000.00000000",
    });
    web::Json(tickers)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Simulate Binance API
    HttpServer::new(|| App::new().route("/api/v3/ticker/bookTicker", web::get().to(get_tickers)))
        // 2 Threads, same as C++
        .workers(2)
        .keep_alive(std::time::Duration::from_secs(100))
        .bind(("0.0.0.0", 8080))?
        .run()
        .await
}
