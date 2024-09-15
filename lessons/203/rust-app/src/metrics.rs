use prometheus_client::encoding::EncodeLabelSet;
use prometheus_client::metrics::family::Family;
use prometheus_client::metrics::histogram::Histogram;
use prometheus_client::registry::Registry;

pub struct AppState {
    pub registry: Registry,
}

#[derive(Clone, Debug, Hash, PartialEq, Eq, EncodeLabelSet)]
pub struct OperationLabels {
    pub op: &'static str,
}

pub struct Metrics {
    pub request: Family<OperationLabels, Histogram>,
}

impl Metrics {
    pub fn observe(&self, op: &'static str, duration: f64) {
        self.request
            .get_or_create(&OperationLabels { op })
            .observe(duration)
    }
    pub fn new() -> Self {
        Metrics {
            request: Family::new_with_constructor(create_histogram),
        }
    }
}

impl AppState {
    pub fn new() -> AppState {
        AppState {
            registry: Registry::default(),
        }
    }
}

pub fn create_histogram() -> Histogram {
    let buckets = [
        0.001, 0.002, 0.003, 0.004, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045,
        0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.15, 0.2, 0.25, 0.3,
        0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 2.0, 3.0, 4.0,
        5.0,
    ];

    Histogram::new(buckets.into_iter())
}
