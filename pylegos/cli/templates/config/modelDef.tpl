;
; This definition file holds the initial model definitions for those used in this project. For a complete description and examples of defining models, see
; the README file located in this same directory.
;
; Attribute Options Key
;------------------------------------------------------------------------------------------------------------------------------------------------------------------
; KEY                   MANDATORY   LEVEL   DEFAULT                 DESCRIPTION
;------------------------------------------------------------------------------------------------------------------------------------------------------------------
;T=Datatype             No          Field   Default=String          -- Valid types are (boolean, string, integer, float, large_string, large_binary, date, timestamp)
;N=Nullable             No          Field   Default=N               -- Indicator to whether field can have nulls
;U=Unique               No          Field   Default=N               -- Indicator to add unique constraint
;I=Index                No          Field   Default=N               -- Indicator to index the field
;S=Size                 No          Field   Defaults string = 255   -- Defines the size constraints for the datatype (only applicable for string and float)
                                                     float = *,2
;D=Default Value        No          Field   Default=None            -- A value to set as default, if string, must be enclosed in single-quotes
;V=Valid Values         No          Field   Default=None            -- (i.e. 'Y','N' OR 'Small', 'Medium', 'Large')
;F=Convert Function     No          Field   Default=None            -- (Any single arg SQL function.  i.e. upper,lower)
;R=References           No          Field   Default=None            -- Name of referencing object, make sure to use object name
;RF=ReferencedField     No          Field   Default=ID              -- Name of the field of referencing table
;RD=RefDeleteOption     No          Field   Default=None            -- The option to use for a delete operation (CASCADE, SET NULL, NONE)
;P=Persistent           No          Object  Default=Y               -- Indicates that the object is persistent and database objects will be created
;S=Sequence             No          Object  Default=100             -- Sets the sequence start value for the table sequence
;------------------------------------------------------------------------------------------------------------------------------------------------------------------
;

#******************************************************************************************
# DO NOT REMOVE DEFAULT MODELS
#******************************************************************************************

AppProperty: {
  propertyName: u=y
  propertyValue: s=400
}

SchemaDeploy: {
  deployVersion: s=25
  deployOperator: s=50
}

SchemaDeployLog: {
  schemaDeployId: r=SchemaDeploy
  scriptName:
  objectOperation: v='CREATE','ALTER','DROP','REPLACE'
  objectName: s=30
  statement: s=4000
  runSuccess: t=boolean
}

#******************************************************************************************
# END OF DEFAULT MODELS
#******************************************************************************************

-- START APPLICATION MODELS HERE



