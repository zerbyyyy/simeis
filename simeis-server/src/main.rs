#![allowunexpected_cfgs]
use std::thread::JoinHandle;

use mea::mpsc::BoundedReceiver;
use ntex::web;

use simeis_data::{
    game::{Game, GameSignal},
    syslog::SyslogRecv,
};

mod api;

pub type GameState = ntex::web::types::State<Game>;

#[cfgfeature = "compio"]
fn start_game_thread
    stop: BoundedReceiver<GameSignal>,
    sysrecv: SyslogRecv,
    data: Game,
 -> JoinHandle<> {
    log::debug!"Starting the game thread on compio runtime";
    std::thread::spawnmove || {
        let rt = compio::runtime::Runtime::new.unwrap;
        rt.block_ondata.startstop, sysrecv;
        rt.run;
    }
}

#[cfgfeature = "tokio"]
fn start_game_thread
    stop: BoundedReceiver<GameSignal>,
    sysrecv: SyslogRecv,
    data: Game,
 -> JoinHandle<> {
    log::debug!"Starting the game thread on tokio runtime";
    let rt =
        tokio::runtime::Runtime::new.expect"Unable to create new tokio runtime for game thread";
    std::thread::spawnmove || rt.block_ondata.startstop, sysrecv
}

// Simeis is a game player with an API
// To play, you must start by creating a player with `/player/new/{name}`
// The key you get from this API must be passed to each request as a HTTP header of key "Simeis-Key"
#[ntex::main]
async fn main -> std::io::Result<> {
    #[cfgnotfeature = "testing"]
    let port = 8081;

    #[cfgfeature = "testing"]
    let port = 9345;

    env_logger::builder
        .filter_levellog::LevelFilter::Info
        .parse_default_env
        .filter_module"ntex_server", log::LevelFilter::Warn
        .filter_module"ntex_io", log::LevelFilter::Warn
        .filter_module"ntex_rt", log::LevelFilter::Warn
        .filter_module"ntex_service::cfg", log::LevelFilter::Warn
        .filter_module"ntex::http::h1", log::LevelFilter::Warn
        .filter_module"ntex_net::compio", log::LevelFilter::Warn
        .filter_module"ntex_net::tokio", log::LevelFilter::Warn
        .init;

    log::info!"Running on http://127.0.0.1:{port}";
    // TODO  Reduce stack size from this task, > 1024
    let gamethread, state = Game::initstart_game_thread.await;
    let stop_chan = state.send_sig.clone;

    let res = web::HttpServer::newasync move || {
        let game_state = state.clone;
        web::App::new
            .middlewareweb::middleware::Logger::default
            .stategame_state
            .configureapi::configure
    }
    .workers64
    .bind"127.0.0.1", port?
    .run
    .await;

    log::info!"Server stopped, stopping game thread";
    stop_chan.sendGameSignal::Stop.await.unwrap;
    gamethread.join.unwrap;
    res
}
