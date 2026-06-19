use std::str::FromStr;

use ntex::router::IntoPattern;
use ntex::web;
use ntex::web::scope;
use ntex::web::types::Path;
use ntex::web::HttpRequest;
use ntex::web::ServiceConfig;

use serde_json::json;
use serde_json::to_value;
use simeis_data::galaxy::station::StationId;

use simeis_data::errors::Errcode;
use simeis_data::ship::resources::Resource;

use crate::api::build_response;
use crate::api::GameState;

// @summary Get prices of each resources on the market
// @returns The price for each resource
#[web::get"/prices"]
async fn get_market_pricessrv: GameState -> impl web::Responder {
    let res = srv.market.to_json.await;
    build_responseOkres
}

// @summary Buy a specific resource on the market
// @returns How much was added to the cargo, how much money was removed, and the amount of fees
#[web::post"/{station_id}/buy/{resource}/{amnt}"]
async fn buy_resource
    srv: GameState,
    args: Path<StationId, String, f64>,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, resource, amnt = args.clone;
    let Okresource = Resource::from_str&resource else {
        return build_responseErrErrcode::InvalidArgument"resource";
    };
    let data = srv
        .player_market_buy&pkey, &station_id, &resource, amnt
        .await
        .map|tx| to_valuetx.unwrap;
    build_responsedata
}

// @summary Sell a specific resource on the market
// @returns How much was removed from the cargo, how much money was added, and the amount of fees
#[web::post"/{station_id}/sell/{resource}/{amnt}"]
async fn sell_resource
    srv: GameState,
    args: Path<StationId, String, f64>,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, resource, amnt = args.clone;
    let Okresource = Resource::from_str&resource else {
        return build_responseErrErrcode::InvalidArgument"resource";
    };
    let data = srv
        .player_market_sell&pkey, &station_id, &resource, amnt
        .await
        .map|tx| to_valuetx.unwrap;
    build_responsedata
}

// Depends on the level of the trader
// @summary Get the fee rate applied on the market of a station
// @returns The fee rate
#[web::get"/{station_id}/fee_rate"]
async fn get_fee_rate
    srv: GameState,
    station_id: Path<StationId>,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let data = srv
        .map_station&pkey, &station_id, |pid, station| {
            Box::pinasync move {
                let rate = station.get_fee_ratepid.await?;
                Okjson!{ "fee_rate": rate }
            }
        }
        .await;
    build_responsedata
}

pub fn configure<T: IntoPattern>base: T, srv: &mut ServiceConfig {
    srv.service
        scopebase
            .serviceget_fee_rate
            .serviceget_market_prices
            .servicebuy_resource
            .servicesell_resource,
    ;
}
