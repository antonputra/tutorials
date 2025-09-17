use axum::{Json, http::StatusCode, response::IntoResponse};

use crate::models::Ticker;

/// Returns a list of connected devices.
pub async fn get_tickers() -> impl IntoResponse {
    // Preallocate vector with exact capacity same as C++ & other Rust frameworks.
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

    (StatusCode::OK, Json(tickers))
}
