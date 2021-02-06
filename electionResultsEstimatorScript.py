# Name:  electionResultsEstimatorScript.py
# Author:  Ismael Rodriguez
# Date: 20 DEC 2019
# Extensions and Licenses:  This script requires ESRI Spatial Analysis Extension
# Description:  This free-standing script creates and exports a table of estimated election results for a user selected feature class within the state of Kansas.  


# Import required modules.

import arcpy, os, sys

import pandas as pd

# Set environment variables

arcpy.env.overwriteOutput = True # Overwrite output.



# Set current scratch workspace.

arcpy.env.workspace = "C:\\Users\\ismae\\OneDrive - Kansas State University\\finalProjectRodriguez\\toolData\\" 
##arcpy.env.workspace = arcpy.GetParameterAsText(0) #for use with scriptTool

arcpy.env.mask ="kansasBoundary.shp"  

arcpy.env.extent ="kansasBoundary.shp" 

# Verify Extensions: Confirm correct ArcGIS software extension.  Check out "Spatial Extension"

if arcpy.CheckExtension("Spatial")=="Available":  # tests for availability of Spatial Analyst Extension and, if available, checks out extension
    print("Spatial Analyst extension is Available.")
    arcpy.CheckOutExtension("Spatial")
    print("You have checked out Spatial Analyst Extension.")

else:  
    print "Extension Error:  Spatial analyst extension is not available."  # Message Option 1:  Extension Error


try:
    
    geography = "kansasCounty_CB_2018.shp"
    ##geography = "kansasUpperLegDist.shp"
    ##geography = "kansasLowerLegDist.shp"
    ##geography = "kansasSchoolDist.shp"
    ##geography = "kansasZipCode2018.shp"
    ##geograpyy = "kansas116Congress.shp"
    ##geography = "kansasCountySubDist.shp"
    ##geography = arcpy.GetParameterAsText(1) #User selected Kansas-wide shapefile.  For use with scriptTool
    
    geoIndex = "AFFGEOID" #For use with all geographies except zip codes(AFFGEOID10), congressional districts(GEOID)
    ##geoIndex = arcpy.GetParameterAsText(2) #User selected index field within selected shapefile.  Default is AFFGEOID.  For use with scriptTool
    ##geoIndex = "AFFEOID10" #for use "kansasZipCode2018.shp"
    ##geoIndex = "GEOID" #for use with "kansas116Congress.shp"
    
    filename = os.path.splitext(os.path.basename(geography)) #for naming conventions
    directory = os.path.split(os.path.dirname(geography)) #for naming conventions
    geoPoints = filename[0]+"Points_TEST.shp" #for  naming conventions
    outworkspace = "C:\\Users\\ismae\\OneDrive - Kansas State University\\finalProjectRodriguez\\scratch\\" 


    arcpy.FeatureToPoint_management(geography,geoPoints,"CENTROID") #Generates a point shapefile with points centroids of user selected shapefile
    messageA = arcpy.GetMessageCount()
    print "FeatureToPoint Tool: " + arcpy.GetMessage(messageA-1)


    rasterFolder = arcpy.ListFiles("*.tif") #Creates a folder of raster tif files

    # This for loop builds a list of raster files and associated index labels.  targetSet = ['indexRaster.tif','index']
    targetSet = []
    for rasterFile in rasterFolder:
        rasterName = os.path.splitext(os.path.basename(rasterFile))
        voteName = rasterName[0]
        geographyRaster = arcpy.sa.ZonalStatistics(geography,geoIndex,rasterFile,"SUM","DATA") #estimates total votes for specified geography
        geographyRaster.save(os.path.join(outworkspace, filename[0] +"_"+ rasterName[0] +".tif"))
        rasterSet = [geographyRaster, voteName[7:]]
        targetSet.append(rasterSet)

    #Builds a point based feature class that includes the extracted values from the selected rasters.  
    arcpy.sa.ExtractMultiValuesToPoints(geoPoints,targetSet,"NONE")
    message2 = arcpy.GetMessageCount()
    print "ExtractMultiValuesToPoints Tool: " + arcpy.GetMessage(message2-1)

    #Extracts the tabular information from the point file into a csv formatted table. 
    geographyTable = filename[0]+"_Table.csv"
    arcpy.TableToTable_conversion(geoPoints,outworkspace,geographyTable)
    arcpy.DeleteFeatures_management(geoPoints)
    messageC = arcpy.GetMessageCount()
    print "TableToTable_Conversion Tool: " + arcpy.GetMessage(messageC-1)
    print "Table saved as csv file: "+ outworkspace+geographyTable


except arcpy.ExecuteError:
    print arcpy.GetMessages(2)

finally:
    arcpy.CheckInExtension("Spatial")
    print "You have checked in Spatial Analyst Extension."

# Data cleaning, transformation, and visualization using Python Pandas module
fullPath = outworkspace+geographyTable
#fullPath = outworkspace+"\\"+geographyTable
sd = pd.read_csv(fullPath) #loads csv file into pandas dataframe

# Transforms column names and create new dataframe to compare primary presidential candidates.  
sd.rename(columns={'G16PREDCLI': 'Clinton', 'G16PRERTRU': 'Trump','G16PRELJOH': 'Johnson'}, inplace=True)
sd2 = sd[['Clinton','Trump']]

# Cleans data to include only positive values
sd3 = sd2[(sd2['Clinton']>0) & (sd2['Trump']>0)]

# Creates and saves area plot
areaPlot = sd3.plot.area(stacked=False,figsize=(32,24))
fig = areaPlot.get_figure()
fig.savefig(outworkspace+filename[0]+"_areaPlot.png")
print "Area plot saved as png file: "+ outworkspace+filename[0]+"_areaPlot.png"

# Creates and saves box plot
boxPlot =sd3.plot.box()
figTwo = boxPlot.get_figure()
figTwo.savefig(outworkspace+filename[0]+"_boxPlot.png")
print "Box plot saved as png file: "+ outworkspace+filename[0]+"_boxPlot.png"