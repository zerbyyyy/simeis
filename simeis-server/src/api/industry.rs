use std::collections::BTreeMap;
use std::str::FromStr;

use ntex::router::IntoPattern;
use ntex::web;
use ntex::web::scope;
use ntex::web::types::Path;
use ntex::web::HttpRequest;
use ntex::web::ServiceConfig;

use serde_json::json;
use serde_json::to_value;

use simeis_data::errors::Errcode;
use simeis_data::galaxy::station::StationId;
use simeis_data::industry::IndustryUnitId;
use simeis_data::industry::IndustryUnitType;
use strum::IntoEnumIterator;

use crate::api::build_response;
use crate::api::GameState;

// @summary List all the industry units available to buy on the station
// @returns The price for each unit
#[web::get"/buy"]
async fn list_buy_industry
    args: Path<StationId>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id = *args;

    let data = srv
        .map_player&pkey, |player| {
            Box::pinasync move {
                let Some_station = player.stations.get&station_id.cloned else {
                    return ErrErrcode::NoSuchStationstation_id;
                };
                let mut res: BTreeMap<IndustryUnitType, f64> = BTreeMap::new;
                for unit in IndustryUnitType::iter {
                    let price = unit.get_price_buy;
                    res.insertunit, price;
                }
                Okto_valueres.unwrap
            }
        }
        .await;
    build_responsedata
}

// @summary Buy a new industry unit
// @returns The ID of the unit bought, and the cost of the transaction
#[web::post"/buy/{name}"]
async fn buy_industry
    args: Path<StationId, String>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, indutype = args.clone;
    let Okindutype = IndustryUnitType::from_strindutype.as_str else {
        return build_responseErrErrcode::InvalidArgument"industry_type";
    };

    let data = srv
        .map_player_mut&pkey, |player| {
            Box::pinasync move {
                let Somestation = player.stations.get&station_id.cloned else {
                    return ErrErrcode::NoSuchStationstation_id;
                };
                let id, cost = station.buy_industryplayer, indutype.await?;
                Okjson!{ "id": id, "cost": cost }
            }
        }
        .await;
    build_responsedata
}

// @summary Upgrade an industry unit
// @returns The new rank of the industry unit
#[web::post"/upgrade/{industry_id}"]
async fn upgrade_industry
    args: Path<StationId, IndustryUnitId>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, id = *args;

    let data = srv
        .map_player_mut&pkey, |player| {
            Box::pinasync move {
                let Somestation = player.stations.get&station_id.cloned else {
                    return ErrErrcode::NoSuchStationstation_id;
                };
                let newrank = station.upgrade_industryplayer, &id.await?;
                Okjson!{ "new-rank": newrank }
            }
        }
        .await;
    build_responsedata
}

// @summary Start an industry unit
// @returns Nothing
// Unless started, an industry unit will NOT produce anything
#[web::post"/start/{industry_id}"]
async fn start_industry
    args: Path<StationId, IndustryUnitId>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, id = *args;

    let data = srv
        .map_station&pkey, &station_id, |pid, station| {
            Box::pinasync move {
                station.start_industrypid, &id.await?;
                Okto_value.unwrap
            }
        }
        .await;
    build_responsedata
}

// @summary Stop an industry unit
// @returns Nothing
#[web::post"/stop/{industry_id}"]
async fn stop_industry
    args: Path<StationId, IndustryUnitId>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, id = *args;

    let data = srv
        .map_station&pkey, &station_id, |pid, station| {
            Box::pinasync move {
                station.stop_industrypid, &id.await?;
                Okto_value.unwrap
            }
        }
        .await;
    build_responsedata
}

// @summary Shows the production inputs & outputs of a particular unit
// @returns The resources needed in input of the unit, and the one produced in the output
#[web::get"/production/{industry_id}"]
async fn show_production
    args: Path<StationId, IndustryUnitId>,
    srv: GameState,
    req: HttpRequest,
 -> impl web::Responder {
    let pkey = get_player_key!req;
    let station_id, id = *args;

    let data = srv
        .map_station&pkey, &station_id, |pid, station| {
            Box::pinasync move {
                let inputs, outputs = station.get_industry_productionpid, id.await?;
                Okjson!{
                    "inputs": to_valueinputs.unwrap,
                    "outputs": to_valueoutputs.unwrap,
                }
            }
        }
        .await;

    build_responsedata
}

pub fn configure<T: IntoPattern>base: T, srv: &mut ServiceConfig {
    srv.service
        scopebase
            .servicelist_buy_industry
            .servicebuy_industry
            .serviceupgrade_industry
            .serviceshow_production
            .servicestart_industry
            .servicestop_industry,
    ;
}
