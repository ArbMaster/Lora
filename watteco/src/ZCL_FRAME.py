# -*- coding: utf-8 -*-

from ZCL import *
#from BATCH_FRAME import *


#### FULL Standard frame description ####################e####
STDFrame = Struct(
	"FrameCtrl" / FrameCtrl,
	"CommandID" / CommandID,
	"ClusterID" / ClusterID,
	
	#Report
	Embedded ( 
		If ( ((this.CommandID == "ReportAttributesAlarm") |(this.CommandID == "ReportAttributes")),
			Struct(		"AttributeID" / AttributeID,
						"AttributeType" / DataType,
						"Data" / Data,
						"Cause" / GreedyRange(CauseRP)
			)
		)
	),
	#configure reporting
	Embedded ( 
		If ( (this.CommandID == "ConfigureReporting") ,
			Struct(		"ReportParameters" / ReportParameters,
						"AttributeID" / AttributeID,
						"AttributeType" / DataType,
						"MinReport" / MinMaxField,
						"MaxReport" / MinMaxField,
						#if New configure report
						 Embedded ( 	If ( 	((this.AttributeType == "CharString") |
									(this.AttributeType  == "ByteString") |
									(this.AttributeType  == "LongByteString") |
									(this.AttributeType  == "StructOrderedSequence")) & (this.ReportParameters.New == "Yes")
								, Struct("Size" / Int8ub)
							)
						),
						Embedded (If ((this.ReportParameters.New == "Yes") & (this.ReportParameters.NoHeaderPort == "Yes"),Struct("Port" / Byte))),
						Embedded (If ((this.ReportParameters.New == "Yes") , Struct("Cause" / GreedyRange(CauseConfiguration)))),
						#if Old configure report
						"Data" / If ((this.ReportParameters.New == "No") ,  Data ),

			)
		)
	),
	#configure reporting response
	Embedded ( 
		If ( ((this.CommandID == "ConfigureReportingResponse")),
			Struct(		"Status" / Status,
						"ReportParameters" / ReportParameters,
						"AttributeID" / AttributeID,
			)
		)
	),
	
	#Read reporting Configuration
	Embedded ( 
		If ( (this.CommandID == "ReadReportingConfiguration"),
			Struct(		"ReportParameters" / ReportParameters,
						"AttributeID" / AttributeID
			)
		)
	),
	#Read reporting Configuration response
	Embedded ( 
		If ( ((this.CommandID == "ReadReportingConfigurationResponse")),
			Struct(		"Status" / Status,
						"ReportParameters" / ReportParameters,
						"AttributeID" / AttributeID,
						"AttributeType" / DataType,
						"MinReport" / MinMaxField,
						"MaxReport" / MinMaxField,
						 Embedded ( 	If ( 	(this.AttributeType == "CharString") |
												(this.AttributeType  == "ByteString") |
												(this.AttributeType  == "LongByteString") |
												(this.AttributeType  == "StructOrderedSequence")
											, Struct("Size" / Int8ub)
										)
						),
						Embedded (If ((this.ReportParameters.New == "Yes") & (this.ReportParameters.NoHeaderPort == "Yes"),Struct("Port" / Byte))),
						Embedded (If ((this.ReportParameters.New == "Yes") , Struct("Cause" / GreedyRange(CauseConfiguration)))),
						"Data" / If ((this.ReportParameters.New == "No") ,  Data ),
			)
		)
	),
	
	
	#Read Attribut request
	Embedded ( 
		If ( ((this.CommandID == "ReadAttribute")),
			Struct(		
						"AttributeID" / AttributeID,
			)
		)
	),
	
	#Read Attribut response
	Embedded ( 
		If ( ((this.CommandID == "ReadAttributeResponse")),
			Struct(		
						"AttributeID" / AttributeID,
						"Status" / Status,
						"AttributeType" / DataType,
						"Data" / Data
			)
		)
	),
	
	#Write Attribut no response
	Embedded ( 
		If ( ((this.CommandID == "WriteAttributeNoResponse")),
			Struct(		
						"AttributeID" / AttributeID,
						"AttributeType" / DataType,
						"Data" / Data
			)
		)
	),
	
	#Cluster Specific Command
	Embedded ( 
		If ( ((this.CommandID == "ClusterSpecificCommand")),
			Struct(		
						"Data" / GreedyRange(Byte)
			)
		)
	),
)




