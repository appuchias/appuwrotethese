CREATE VIEW gas_prices AS (
    SELECT id_eess, date, company, address, latitude, longitude, locality_id, province_id, postal_code, schedule,
           price_goa, price_gob, price_g95e5, price_g95e5_premium, price_g95e10, price_g98e5, price_g98e10, price_glp, price_gnc, price_h2
    FROM gas_station gs
    JOIN gas_stationprice gsp ON gs.id_eess == gsp.station_id
);
