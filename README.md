# canada-hydrographs
dash app that shows Canadian hydrograph data, as well as ERA5 rain fall reanalysis data

available here: https://canada-hydrographs.herokuapp.com/

station discharge/level data is from the National Water Data Archive: https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services/national-archive-hydat.html

rain data is from ERA5 reanalysis product total precipitation converted to mm/day: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview

data is preprocessed into a form easy to access in app.py. date range is 2005-01-01 to 2017-12-31. there is one discharge, level, and rain fall value per day per station (if data does not exist, it is nan). 

CSS layout of app is from: https://codepen.io/chriddyp/pen/bWLwgP

app can be deployed on your own server or using heroku via git (https://devcenter.heroku.com/articles/git)
