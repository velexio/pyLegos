; Comment lines can start with (#,;,--)
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
; Object Definition Syntax
; ------------------------------------------------------
; <object name>: <c|category>=<cat>;[S=<start value>] {
; fieldOne: T=<datatype>;M=<maxsize>;U=<Y|N>;
; fieldTwo: T=<datatype>;
; fieldThree: t=integer; r=<referenced object name>; rf=<referenced field>; rd=<delete option>;
; }
; ------------------------------------------------------
;
; NOTES: Attribute options are not case-sensitive. (i.e. T=Boolean and t=boolean are valid)
;        You specify the attribute option with either the shortcut or full name. (i.e T=Boolean and Datatype=Boolean are equivalent)
;        *** If persistence is set to 'N', then of course you do not need to set attributes on the object fields
;        *** DO NOT SPECIFY A PK FIELD OR CREATED/MODIFIED AS THESE ARE AUTOMATICALLY CREATED BY GENERATOR
;            AND NAMED BY STANDARD CONVENTION.
;        *** All object names should be singular.  By convention, table names (because a table represents a collection of objects,
;            will be pluralized by the generator
;        *** Define object names using InitCap naming format and attributes as camel case, which is standard coding convention.
;        *** If you define a attribute as unique, by default it will not be allowed to have nulls and the convert
;            function will be set to lower by default
;        *** If you define a attribute w/ a reference, it will be set to not null by default (unless specified)
;            and it will be indexed
;
; DISCLAIMER - This tool is meant to limit the amount of "boilerplate" code that is needed to be created.  It
;              covers roughly 95% of typical use cases for most application model objects and database tables.  It
;              does not support features such as composite unique keys, many-to-many relationships, composite
;              indexes, etc.  It is anticipated that output will be changed, amended from time to time.

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



