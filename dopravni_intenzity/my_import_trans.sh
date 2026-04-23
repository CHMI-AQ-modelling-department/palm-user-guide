#!/bin/bash

SHAPEFILE_DIR="/storage/home/gunes/data/palm/dopravni_intenzity"

ogr2ogr \
  -nln "transportation_legerova"."main_roads" \
  -lco GEOMETRY_NAME=geom \
  -lco FID=gid \
  -lco PRECISION=NO \
  -nlt PROMOTE_TO_MULTI \
  -a_srs EPSG:32633 \
  Pg:"dbname=my_palm_transportation host=localhost user=postgres port=5432" \
  "$SHAPEFILE_DIR/liniove_zdroje_22_utm.shp"

ogr2ogr \
  -nln "transportation_legerova"."aux_roads" \
  -lco GEOMETRY_NAME=geom \
  -lco FID=gid \
  -lco PRECISION=NO \
  -nlt PROMOTE_TO_MULTI \
  -a_srs EPSG:32633 \
  Pg:"dbname=my_palm_transportation host=localhost user=postgres port=5432" \
  "$SHAPEFILE_DIR/vedlejsi_proemi3.shp"
