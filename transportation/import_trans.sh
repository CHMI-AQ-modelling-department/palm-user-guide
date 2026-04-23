#!/bin/bash

# export PGPASSWORD=mydatabasepassword

ogr2ogr \
  -nln "trans_legerova"."line_sources_main" \
  -lco GEOMETRY_NAME=geom \
  -lco FID=gid \
  -lco PRECISION=NO \
  Pg:"dbname=palm_trans host=localhost user=resler port=5432" \
  liniove_zdroje_22_utm.shp

# -nlt PROMOTE_TO_MULTI \


ogr2ogr \
  -nln "trans_legerova"."line_sources_aux" \
  -lco GEOMETRY_NAME=geom \
  -lco FID=gid \
  -lco PRECISION=NO \
  Pg:"dbname=palm_trans host=localhost user=resler port=5432" \
  vedlejsi_proemi3.shp
