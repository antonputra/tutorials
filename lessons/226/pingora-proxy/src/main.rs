mod config;

use async_trait::async_trait;
use log::debug;
use pingora::prelude::*;
use std::sync::Arc;

use pingora::listeners::tls::TlsSettings;

use self::config::Config;

fn main() {
    env_logger::init();
    let cfg = Config::load("Proxy.toml");

    let mut my_server = Server::new(Some(Opt::parse_args())).unwrap();
    my_server.bootstrap();

    let mut upstreams = LoadBalancer::try_from_iter(cfg.proxy.upstreams).unwrap();

    let hc = TcpHealthCheck::new();
    upstreams.set_health_check(hc);
    upstreams.health_check_frequency = Some(std::time::Duration::from_secs(5));

    let background = background_service("health check", upstreams);
    let upstreams = background.task();

    let mut lb = http_proxy_service(&my_server.configuration, LB(upstreams));

    let mut tls_settings =
        TlsSettings::intermediate(&cfg.proxy.tls_cert, &cfg.proxy.tls_key).unwrap();
    tls_settings.enable_h2();

    lb.add_tls_with_settings(
        format!("0.0.0.0:{}", cfg.proxy.port).as_str(),
        None,
        tls_settings,
    );

    my_server.add_service(background);
    my_server.add_service(lb);
    my_server.run_forever();
}

pub struct LB(Arc<LoadBalancer<RoundRobin>>);

#[async_trait]
impl ProxyHttp for LB {
    type CTX = ();
    fn new_ctx(&self) -> () {
        ()
    }

    async fn upstream_request_filter(
        &self,
        session: &mut Session,
        upstream_request: &mut RequestHeader,
        _ctx: &mut Self::CTX,
    ) -> Result<()> {
        let client_addr = session.client_addr().unwrap();
        upstream_request
            .insert_header("X-Forwarded-For", client_addr.to_string())
            .unwrap();
        Ok(())
    }

    async fn upstream_peer(&self, _session: &mut Session, _ctx: &mut ()) -> Result<Box<HttpPeer>> {
        let upstream = self.0.select(b"", 256).unwrap();

        debug!("upstream peer is: {upstream:?}");

        let peer = Box::new(HttpPeer::new(upstream, false, "".to_string()));
        Ok(peer)
    }
}
