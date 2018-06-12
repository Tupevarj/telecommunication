/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2012 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Manuel Requena <manuel.requena@cttc.es>
 */

#ifndef EPC_X2_SAP_H
#define EPC_X2_SAP_H

#include "ns3/packet.h"
#include "ns3/eps-bearer.h"
#include "ns3/ipv4-address.h"

#include <bitset>

namespace ns3 {


class Node;

/**
 * The X2 SAP defines the service between the X2 entity and the RRC entity.
 * 
 * The X2 SAP follows the specification 3GPP TS 36.423: "X2 application protocol (X2AP)"
 * 
 * The service primitives corresponds to the X2AP procedures and messages and 
 * the service parameters corresponds to the Information Elements
 * 
 * Note: Any reference in this file refers to the 3GPP TS 36.423 specification
 */

/**
 * \brief Common structures for EpcX2SapProvider and EpcX2SapUser
 */
class EpcX2Sap
{
public:
  virtual ~EpcX2Sap ();
  
  /**
   * E-RABs to be setup item as
   * it is used in the HANDOVER REQUEST message.
   * See section 9.1.1.1 for further info about the parameters
   */
  struct ErabToBeSetupItem
  {
    uint16_t    erabId; ///< E-RAB ID
    EpsBearer   erabLevelQosParameters; ///< E-RAB level QOS parameters
    bool        dlForwarding; ///< DL forwarding
    Ipv4Address transportLayerAddress; ///< transport layer address
    uint32_t    gtpTeid; ///< TEID

    ErabToBeSetupItem ();
  };

  /**
   * E-RABs admitted item as
   * it is used in the HANDOVER REQUEST ACKNOWLEDGE message.
   * See section 9.1.1.2 for further info about the parameters
   */
  struct ErabAdmittedItem
  {
    uint16_t    erabId; ///< E-RAB ID
    uint32_t    ulGtpTeid; ///< uplink GTP TEID
    uint32_t    dlGtpTeid; ///< downlink GTP TEID
  };

  /**
   * E-RABs not admitted item as
   * it is used in the HANDOVER REQUEST ACKNOWLEDGE message.
   * See section 9.1.1.2 for further info about the parameters
   */
  struct ErabNotAdmittedItem
  {
    uint16_t    erabId;///< E-RAB ID
    uint16_t    cause;///< cause
  };

  /**
   * E-RABs subject to status transfer item as
   * it is used in the SN STATUS TRANSFER message.
   * See section 9.1.1.4 for further info about the parameters
   */
  static const uint16_t m_maxPdcpSn = 4096;

  /// ErabsSubjectToStatusTransferItem structure
  struct ErabsSubjectToStatusTransferItem
  {
    uint16_t            erabId; ///< ERAB ID
    std::bitset<m_maxPdcpSn> receiveStatusOfUlPdcpSdus; ///< receive status of UL PDCP SDUs
    uint16_t            ulPdcpSn; ///< UL PDCP SN
    uint32_t            ulHfn; ///< UL HFN
    uint16_t            dlPdcpSn; ///< DL PDCP SN
    uint32_t            dlHfn; ///< DL HFN
  };

  /**
   * UL Interference OverloadIndication as
   * it is used in the LOAD INFORMATION message.
   * See section 9.2.17 for further info about the values
   */
  enum UlInterferenceOverloadIndicationItem
  {
    HighInterference,
    MediumInterference,
    LowInterference
  };

  /**
   * UL High Interference Information as
   * it is used in the LOAD INFORMATION message.
   * See section 9.1.2.1 for further info about the parameters
   */
  struct UlHighInterferenceInformationItem
  {
    uint16_t    targetCellId; ///< target cell ID
    std::vector <bool> ulHighInterferenceIndicationList; ///< UL high interference indication list
  };

  /**
   * Relative Narrowband Tx Power (RNTP) as
   * it is used in the LOAD INFORMATION message.
   * See section 9.2.19 for further info about the parameters
   * 
   * Note: You can use INT16_MIN value for -infinite value
   *       in the rntpThreshold field
   */
  struct RelativeNarrowbandTxBand
  {
    std::vector <bool> rntpPerPrbList; ///< RNTP per prb list
    int16_t     rntpThreshold; ///< RNTP threshold
    uint16_t    antennaPorts; ///< antenna ports
    uint16_t    pB; ///< PB
    uint16_t    pdcchInterferenceImpact; ///< PDC channel interference list
  };

  /**
   * Cell Information Item as
   * it is used in the LOAD INFORMATION message.
   * See section 9.1.2.1 for further info about the parameters
   */
  struct CellInformationItem
  {
    uint16_t    sourceCellId; ///< source cell ID
    std::vector <UlInterferenceOverloadIndicationItem> ulInterferenceOverloadIndicationList; ///< UL interference overload indication list
    std::vector <UlHighInterferenceInformationItem> ulHighInterferenceInformationList; ///< UL high interference information list
    RelativeNarrowbandTxBand relativeNarrowbandTxBand; ///< relative narrow transmit band
  };

  /**
   * Load Indicator as
   * it is used in the RESOURCE STATUS UPDATE message.
   * See section 9.2.36 for further info about the value
   */
  enum LoadIndicator
  {
    LowLoad,
    MediumLoad,
    HighLoad,
    Overload
  };

  /**
   * Composite Available Capacity as
   * it is used in the RESOURCE STATUS UPDATE message.
   * See section 9.2.45 for further info about the parameters
   */
  struct CompositeAvailCapacity
  {
    uint16_t    cellCapacityClassValue; ///< cell capacity class value
    uint16_t    capacityValue; ///< capacity value
  };
  /**
   * 9.2.76 RSRP Measurement Report List
   */
  struct RSRPMeasurementResult
  {
	   uint16_t RSRPCellId;
	   uint16_t RSRPMeasured;
  };
  struct RSRPMeasurementReportItem
  {
	   std::vector<RSRPMeasurementResult> rSRPMeasurementResult; // for each neighbour cell for user UE
	   uint16_t uEId;
  };
  /**
   *
   * Cell ID IE is The E-UTRAN Cell Global Identifier (ECGI) is used to globally identify a cell (see TS 36.401 [2]).
   */
  struct CellId
  {
	    uint16_t   cellId;
	   //std::bitset<28> EUTRANCellIdentifier;
	   //octeString<3> PLMNIdentity; // Octetstring : not being currently used.
  };
  /**My****
   * Cell Measurement Result Item as
   * it is used in the RESOURCE STATUS UPDATE message.
   * See section 9.1.2.14 for further info about the parameters
   */
  struct CellMeasurementResultItem
  {

    uint16_t        cellId; ///<  cell id
    //CellId		cellId;       ///< ECGI , to add it remember to modify the header length
    LoadIndicator   dlHardwareLoadIndicator; ///< DL hardware load indicator
    LoadIndicator   ulHardwareLoadIndicator; ///< UL hardware load indicator

    LoadIndicator   dlS1TnlLoadIndicator; ///< DL S1 TNL load indicator
    LoadIndicator   ulS1TnlLoadIndicator; ///< UL S1 TNL load indicator

    uint16_t        dlGbrPrbUsage ; ///< DL GBR PRB usage
    uint16_t        ulGbrPrbUsage; ///< UL GBR PRB usage
    uint16_t        dlNonGbrPrbUsage; ///< DL Non GBR PRB usage
    uint16_t        ulNonGbrPrbUsage; ///< UL Non GBR PRB usage
    uint16_t        dlTotalPrbUsage; ///< DL Total PRB usage
    uint16_t        ulTotalPrbUsage; ///< UL Total PRB usage

    CompositeAvailCapacity  dlCompositeAvailableCapacity; ///< DL composite available capacity
    CompositeAvailCapacity  ulCompositeAvailableCapacity; ///< UL composite available capacity

    std::vector<RSRPMeasurementReportItem> rRSPMeasurementReportList; // for each UE within cell within eNB
  };


  /// Cause ID enumeration
  enum IdCause
  {

  	 HandoverDesirableForRadioReason,
   	 TimeCriticalHandover,
   	 ResourceOptimisationHandover,
   	 ReduceLoadinServingCell,
   	 PartialHandover,
   	 UnknownNeweNBUEX2APID,
   	 UnknownOldeNBUEX2APID,
   	 UnknownPairofUEX2APID ,
   	 HOTargetnotAllowed,
   	 TX2RELOCoverallExpiry,
   	 TRELOCprepExpiry,
   	 CellnotAvailable,
   	 NoRadioResourcesAvailableinTargetCell,
   	 InvalidMMEGroupID,
   	 UnknownMMECode,
		 EncryptionAnd_OrIntegrityProtection,
   	 AlgorithmsNotSupported,
   	 ReportCharacteristicsEmpty,
   	 NoReportPeriodicity,
   	 ExistingMeasurementID,
		 UnknowneNBMeasurementID,
   	 MeasurementTemporarilynotAvailable,
   	 Unspecified,
		 LoadBalancing,
		 HandoverOptimisation,
		 Valueoutofallowedrange,
		 MultipleERABIDinstances,
		 SwitchOffOngoing,
   	 NotsupportedQCIvalue,
   	 Measurementnotsupportedfortheobject,
		 TDCoverallExpiry,
		 TDCprepExpiry,
   	 ActionDesirableforRadioReasons,
   	 ReduceLoad,
   	 ResourceOptimisation,
   	 TimeCriticalaction,
   	 TargetnotAllowed,
   	 NoRadioResourcesAvailable,
   	 InvalidQoScombination,
   	 EncryptionAlgorithmsNotSupported,
		 Procedurecancelled,
   	 RRMpurpose,
   	 Improveuserbitrate,
   	 UserInactivity,
   	 RadioConnectionWithUELost,
   	 FailureintheRadioInterfaceProcedure,
   	 BearerOptionnotSupported
  };


  /**
   * \brief Parameters of the HANDOVER REQUEST message.
   *
   * See section 9.1.1.1 for further info about the parameters
   */
  struct HandoverRequestParams
  {
    uint16_t            oldEnbUeX2apId; ///< old ENB UE X2 AP ID
    uint16_t            cause; ///< cause
    uint16_t            sourceCellId; ///< source cell ID XX
    uint16_t            targetCellId; ///< target cell ID
    uint32_t            mmeUeS1apId; ///< MME UE S1 AP ID
    uint64_t            ueAggregateMaxBitRateDownlink; ///< UE aggregrate max bit rate downlink
    uint64_t            ueAggregateMaxBitRateUplink; ///< UE aggregrate max bit rate uplink  XX
    std::vector <ErabToBeSetupItem> bearers; ///< bearers
    Ptr<Packet>         rrcContext; ///< RRC context
  };

  /**
   * \brief Parameters of the HANDOVER REQUEST ACKNOWLEDGE message.
   *
   * See section 9.1.1.2 for further info about the parameters
   */
  struct HandoverRequestAckParams
  {
    uint16_t            oldEnbUeX2apId; ///< old ENB UE X2 AP ID
    uint16_t            newEnbUeX2apId; ///< new ENB UE X2 AP ID
    uint16_t            sourceCellId; ///< source cell ID
    uint16_t            targetCellId; ///< target cell ID
    std::vector <ErabAdmittedItem> admittedBearers; ///< admitted bearers
    std::vector <ErabNotAdmittedItem> notAdmittedBearers; ///< not admitted bearers
    Ptr<Packet>         rrcContext; ///< RRC context
  };

  /**
   * \brief Parameters of the HANDOVER PREPARATION FAILURE message.
   *
   * See section 9.1.1.3 for further info about the parameters
   */
  struct HandoverPreparationFailureParams
  {
    uint16_t            oldEnbUeX2apId; ///< old ENB UE X2 AP ID
    uint16_t            sourceCellId; ///< source cell ID
    uint16_t            targetCellId; ///< target cell ID
    uint16_t            cause; ///< cause
    uint16_t            criticalityDiagnostics; ///< criticality diagnostics
  };

  /**
   * \brief Parameters of the SN STATUS TRANSFER message.
   *
   * See section 9.1.1.4 for further info about the parameters
   */
  struct SnStatusTransferParams
   {
     uint16_t            oldEnbUeX2apId; ///< old ENB UE X2 AP ID
     uint16_t            newEnbUeX2apId; ///< new ENB UE X2 AP ID
     uint16_t            sourceCellId; ///< source cell ID
     uint16_t            targetCellId; ///< target cell ID
     std::vector <ErabsSubjectToStatusTransferItem> erabsSubjectToStatusTransferList; ///< ERABs subject to status transfer list
   };

   /**
    * \brief Parameters of the UE CONTEXT RELEASE message.
    *
    * See section 9.1.1.5 for further info about the parameters
    */
   struct UeContextReleaseParams
   {
     uint16_t            oldEnbUeX2apId; ///< old ENB UE X2 AP ID
     uint16_t            newEnbUeX2apId; ///< new ENB UE X2 AP ID
     uint16_t            sourceCellId; ///< source cell ID
     uint16_t            targetCellId; ///< target cell ID
   };

   /**
    * \brief Parameters of the LOAD INFORMATION message.
    *
    * See section 9.1.2.1 for further info about the parameters
    */
   struct LoadInformationParams
   {
     uint16_t            targetCellId; ///< target cell ID
     std::vector <CellInformationItem> cellInformationList; ///< cell information list
   };
   /**
      * 9.2.6 Cause The purpose of the cause information element is to indicate the reason for a particular event for the whole protocol.
      */
   //  enum Cause
   //  {


   //  };

    /**
     * from 3GPP TS 36.423 version 13.2.0 Release 13 section 9.2.13
     *  Message Type
     */
   enum MessageType
   {
	  HandoverPreparation,
	  HandoverCancel,
	  LoadIndication,
	  ErrorIndication,
	  SnStatusTransfer,
	  UeContextRelease,
	  X2Setup,
	  Reset,
	  EnbConfigurationUpdate,
	  ResourceStatusReportingInitiation,
	  ResourceStatusReporting,
	  PrivateMessage,
	  MobilitySettingsChange,
	  RadioLinkFailureIndication,
	  HandoverReport,
	  CellActivation,
	  X2Release,
	  X2APMessageTransfer

   };
   /**
    *
    * Registration Request IE
    */
   enum RegistrationRequest
   {
	   Stop,
	   Start
   };

   /**
    * Reporting Periodicity IE
    * the time interval between two subsequent RESOURCE STATUS UPDATE messages that include
    * the Radio Resource Status IE, S1 TNL Load Indicator IE,
    * Hardware Load Indicator IE, Composite Available Capacity Group IE, or ABS Status IE.
    */
   enum ReportingPeriodicity
   {
	   ms1000,
	   ms2000,
	   ms5000,
	   ms10000

   };
   /**
    * Reporting Periodicity of RSRP Measurement Report IE
    */
   enum PeriodicityRSRPMeasurementReport
   {
	   ms120,
	   ms240,
	   ms480,
	   ms640
   };
   /**
    * Reporting Periodicity of CSI Report IE
    */
   enum PeriodicityCSIReport
   {
	   ms5,
	   ms10,
	   ms20,
	   ms40,
	   ms80
   };
   /**
    *
    */
   enum PartialSuccessIndicator
   {
	   NotAllowed,
	   Allowed
   };



   /*
    *  Each position in the bitmap indicates measurement object that failed to be initiated in the eNB 2.
    *  First Bit = PRB Periodic, Second Bit = TNL load Ind Periodic, Third Bit = HW Load Ind Periodic,
    *  Fourth Bit = Composite Available Capacity Periodic, Fifth Bit = ABS Status Periodic,
    *  Sixth Bit = RSRP Measurement ReportPeriodic, Seventh Bit = CSI Report Periodic.
    *  Other bits shall be ignored by the eNB 1 .
    */
   struct MeasurementFailureCauseItem
   {
	      std::bitset<32>     measurementFailedReportCharacteristics;
	      uint8_t 			  cause;
   };


   /**
    * List of cells where measurements were requested
    * included when indicating partial success
    */
   struct MeasurementInitiationResultItem
   {
	  uint16_t            cellId;
	  // CellToReportId	  cellId;  // ECGI
	 // std::vector<MeasurementFailureCauseItem> 	measurementFailureCauseList; // Max number of failed object = 32
	  MeasurementFailureCauseItem 	measurementFailureCauseList; // Max number of failed object = 32


   };

  /**
   * \brief Parameters of the RESOURCE STATUS UPDATE message.
   *
   * See section 9.1.2.14 for further info about the parameters
   */
   struct ResourceStatusUpdateParams
   {
	 uint8_t	     	 messageType =10 ; 		///< ResourceStatusReporting
     uint16_t            enb1MeasurementId; 	///< ENB1 measurement ID
     uint16_t            enb2MeasurementId; 	///< ENB2 measurement ID
     uint16_t            targetEnbId; 			///<  eNB target id
     uint16_t			 sourceEnbId;			///<  eNB source id
     std::vector <CellMeasurementResultItem> cellMeasurementResultList;  ///< cell measurement result list for each cell within eNB
   };

   /**
    * \brief Parameters of the RESOURCE STATUS REQUEST message.
    *
    * See section 9.1.2.11 RESOURCE STATUS REQUEST  MESSAGE for further info about the parameters
    * From section 8.3.6 in 3GPP TS 36.423 version 13.2.0 Release 13
    * Registration Request IE = {start,stop}, if set to "start" then Report Characteristics IE must exists
    * Report Characteristics IE must exists
    * Report Characteristics IE = {7bits}
    * Reporting Periodicity IE its value depends on what is included in Report Characteristics IE
    * Partial Success Indicator IE if it is accepted from eNB2 to provide partial measurements
    * If the eNB2 received a RESOURCE STATUS REQUEST message which includes the Registration Request IE set
    * to "stop", the Cell To Report IE list shall be ignored
    */
    struct ResourceStatusRequestParams
    {
	  uint8_t		  			messageType = 9 ;      ///< ResourceStatusReportingInitiation
      uint16_t            		enb1MeasurementId;     // 2 /< ENB1 measurement ID allocated by eNB1
      uint16_t           		enb2MeasurementId;     // 2 /< ENB2 measurement ID allocated by eNB2

      uint8_t 					regReq;                // 1

      std::bitset<32> 	  		reportCharacteristics; // 4

      std::vector<uint16_t>     targetEnbId;          //(sz*2)  ECGI

      uint16_t					sourceEnbId;

      uint8_t					PSI;                   // 1

      uint8_t 					reportingPeriodicity;  // 1
      uint8_t 					periodicityRSRP;       // 1
      uint8_t 					periodicityCSI;        // 1
    };

 /**MY***********
     * \brief Parameters of the  RESOURCE STATUS RESPONSE MESSAGE.
     * Measurement Initiation Result IE is included if the Partial Success Indicator IE included in request message
     * See section 9.1.2.12 for further info about the parameters
     */
     struct ResourceStatusResponseParams
     {
  	   uint8_t			   messageType = 10; ///< ResourceStatusReportingInitiation

       uint16_t            enb1MeasurementId; ///< ENB1 measurement ID
       uint16_t            enb2MeasurementId; ///< ENB2 measurement ID
       uint16_t			   sourceEnbId;
       // CriticalityDiagnosticsIe   cDIe;    // Optional IE
       uint16_t			   targetEnbId;
       std::vector<MeasurementInitiationResultItem>  measurementInitiationResultList; // max number of cells per eNB = 256

     };
   /**
    * \brief Parameters of the UE DATA primitive
    *
    * Forward UE data during the handover procedure from source eNB (sourceCellId)
    * to target eNB (targetCellId) using a GTP-U tunnel (gtpTeid)
    */
   struct UeDataParams
   {
     uint16_t    sourceCellId; ///< source cell ID
     uint16_t    targetCellId; ///< target cell ID
     uint32_t    gtpTeid; ///< GTP TEID
     Ptr<Packet> ueData; ///< UE data
   };

 };


/**
 * These service primitives of this part of the X2 SAP
 * are provided by the X2 entity and issued by RRC entity
 */
class EpcX2SapProvider : public EpcX2Sap
{
public:
  virtual ~EpcX2SapProvider ();

  //
  // Service primitives
  //

  /**
   * Send handover request function
   * \param params handover request parameters
   */
  virtual void SendHandoverRequest (HandoverRequestParams params) = 0;

  /**
   * Send handover request ack function
   * \param params the handover request ack parameters
   */
  virtual void SendHandoverRequestAck (HandoverRequestAckParams params) = 0;

  /**
   * Send handover preparation failure function
   * \param params the handover preparation failure
   */
  virtual void SendHandoverPreparationFailure (HandoverPreparationFailureParams params) = 0;

  /**
   * Send SN status transfer function
   * \param params the SN status transfer parameters
   */
  virtual void SendSnStatusTransfer (SnStatusTransferParams params) = 0;

  /**
   * Send UE context release function
   * \param params the UE context release parameters
   */
  virtual void SendUeContextRelease (UeContextReleaseParams params) = 0;

  /**
   * Send load information function
   * \param params the load information parameters
   */
  virtual void SendLoadInformation (LoadInformationParams params) = 0;

  /**
   * Send resource status update function
   * \param params the resource statue update paramweters
   */
  virtual void SendResourceStatusUpdate (ResourceStatusUpdateParams params) = 0;


/**
   * Send resource status request function
   * \param params the resource statue request paramweters
   */
  virtual void SendResourceStatusRequest (ResourceStatusRequestParams params) = 0;
 /**
     * Send resource status response function
     * \param params the resource statue response paramweters
     */
  virtual void SendResourceStatusResponse (ResourceStatusResponseParams params) = 0;

  /**
   * Send UE data function
   * \param params the UE data parameters
   */
  virtual void SendUeData (UeDataParams params) = 0;
};


/**
 * These service primitives of this part of the X2 SAP
 * are provided by the RRC entity and issued by the X2 entity
 */
class EpcX2SapUser : public EpcX2Sap
{
public:
  virtual ~EpcX2SapUser ();

  /*
   * Service primitives
   */

  /**
   * Receive handover request function
   * \param params the handover request parameters
   */
  virtual void RecvHandoverRequest (HandoverRequestParams params) = 0;

  /**
   * Receive handover request ack function
   * \param params the handover request ack parameters
   */
  virtual void RecvHandoverRequestAck (HandoverRequestAckParams params) = 0;

  /**
   * Receive handover preparation failure function
   * \param params the handover preparation failure parameters
   */
  virtual void RecvHandoverPreparationFailure (HandoverPreparationFailureParams params) = 0;

  /**
   * Receive SN status transfer function
   * \param params the SN status transfer parameters
   */
  virtual void RecvSnStatusTransfer (SnStatusTransferParams params) = 0;

  /**
   * Receive UE context release function
   * \param params the receive UE context release parameters
   */
  virtual void RecvUeContextRelease (UeContextReleaseParams params) = 0;

  /**
   * Receive load information function
   * \param params the load information parameters
   */
  virtual void RecvLoadInformation (LoadInformationParams params) = 0;
  
  /**
   * Receive resource status update function
   * \param params the resource status update parameters
   */
  virtual void RecvResourceStatusUpdate (ResourceStatusUpdateParams params) = 0;


  /**
   * Receive resource status Request function
   * \param params the resource status Request parameters
   */
  virtual void RecvResourceStatusRequest (ResourceStatusRequestParams params) = 0;
  /**
   * Receive resource status Response function
   * \param params the resource status Response parameters
   */
  virtual void RecvResourceStatusResponse (ResourceStatusResponseParams params) = 0;



  /**
   * Receive UE data function
   * \param params UE data parameters
   */
  virtual void RecvUeData (UeDataParams params) = 0;
};

///////////////////////////////////////

template <class C>
class EpcX2SpecificEpcX2SapProvider : public EpcX2SapProvider
{
public:
	  /**
	   * Constructor
	   *
	   * \param x2 the owner class
	   */
	  EpcX2SpecificEpcX2SapProvider (C* x2);

	  //
	  // Interface implemented from EpcX2SapProvider
	  //

	  /**
	   * Send handover request functon
	   * \param params the hadnover request parameters
	   */
	  virtual void SendHandoverRequest (HandoverRequestParams params);

	  /**
	   * Send handover request ack function
	   * \param params the handover request ack pararameters
	   */
	  virtual void SendHandoverRequestAck (HandoverRequestAckParams params);

	  /**
	   * Send handover preparation failure function
	   * \param params the handover preparation failure parameters
	   */
	  virtual void SendHandoverPreparationFailure (HandoverPreparationFailureParams params);

	  /**
	   * Send SN status transfer function
	   * \param params the SN status transfer parameters
	   */
	  virtual void SendSnStatusTransfer (SnStatusTransferParams params);

	  /**
	   * Send UE context release function
	   * \param params the UE context release parameters
	   */
	  virtual void SendUeContextRelease (UeContextReleaseParams params);

	  /**
	   * Send load information function
	   * \param params the load information parameters
	   */
	  virtual void SendLoadInformation (LoadInformationParams params);

	  /**
	   * Send resource status update function
	   * \param params the resource status update parameters
	   */
	  virtual void SendResourceStatusUpdate (ResourceStatusUpdateParams params);
	  /**
	   * Send resource status Request function
	   * \param params the resource status Request parameters
	   */
	  virtual void SendResourceStatusRequest (ResourceStatusRequestParams params);
	  /**
	   * Send resource status Response function
	   * \param params the resource status Response parameters
	   */
	  virtual void SendResourceStatusResponse (ResourceStatusResponseParams params);

	  /**
	   * Send UE data function
	   * \param params the UE data parameters
	   */


	  virtual void SendUeData (UeDataParams params);

private:
	  EpcX2SpecificEpcX2SapProvider ();
	  C* m_x2; ///< owner class
};

template <class C>
EpcX2SpecificEpcX2SapProvider<C>::EpcX2SpecificEpcX2SapProvider (C* x2)
  : m_x2 (x2)
{
}

template <class C>
EpcX2SpecificEpcX2SapProvider<C>::EpcX2SpecificEpcX2SapProvider ()
{
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendHandoverRequest (HandoverRequestParams params)
{
  m_x2->DoSendHandoverRequest (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendHandoverRequestAck (HandoverRequestAckParams params)
{
  m_x2->DoSendHandoverRequestAck (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendHandoverPreparationFailure (HandoverPreparationFailureParams params)
{
  m_x2->DoSendHandoverPreparationFailure (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendSnStatusTransfer (SnStatusTransferParams params)
{
  m_x2->DoSendSnStatusTransfer (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendUeContextRelease (UeContextReleaseParams params)
{
  m_x2->DoSendUeContextRelease (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendLoadInformation (LoadInformationParams params)
{
  m_x2->DoSendLoadInformation (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendResourceStatusUpdate (ResourceStatusUpdateParams params)
{

  m_x2->DoSendResourceStatusUpdate (params);
}
//MY************
template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendResourceStatusRequest (ResourceStatusRequestParams params)
{
	std::cout<<"Cell Id = "<<params.sourceEnbId<<" In SendResourceStatusRequest "<<std::endl;
  m_x2->DoSendResourceStatusRequest (params);
}
//MY************
template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendResourceStatusResponse (ResourceStatusResponseParams params)
{
  m_x2->DoSendResourceStatusResponse (params);
}


template <class C>
void
EpcX2SpecificEpcX2SapProvider<C>::SendUeData (UeDataParams params)
{
  m_x2->DoSendUeData (params);
}

///////////////////////////////////////
/**
 * EpcX2SpecificEpcX2SapUser
 */
template <class C>
class EpcX2SpecificEpcX2SapUser : public EpcX2SapUser
{
public:
	  /**
	   * Constructor
	   *
	   * \param rrc RRC
	   */
	  EpcX2SpecificEpcX2SapUser (C* rrc);

	  //
	  // Interface implemented from EpcX2SapUser
	  //

	  /**
	   * Receive handover request function
	   * \param params the receive handover request parameters
	   */
	  virtual void RecvHandoverRequest (HandoverRequestParams params);

	  /**
	   * Receive handover request ack function
	   * \param params the receive handover request ack parameters
	   */
	  virtual void RecvHandoverRequestAck (HandoverRequestAckParams params);

	  /**
	   * Receive handover preparation failure function
	   * \param params the receive handover preparation failure parameters
	   */
	  virtual void RecvHandoverPreparationFailure (HandoverPreparationFailureParams params);

	  /**
	   * Receive SN status transfer function
	   * \param params the SN status transfer parameters
	   */
	  virtual void RecvSnStatusTransfer (SnStatusTransferParams params);

	  /**
	   * Receive UE context release function
	   * \param params the UE context release parameters
	   */
	  virtual void RecvUeContextRelease (UeContextReleaseParams params);

	  /**
	   * Receive load information function
	   * \param params the load information parameters
	   */
	  virtual void RecvLoadInformation (LoadInformationParams params);

	  /**
	   * Receive resource status update function
	   * \param params the receive resource status update
	   */
	  virtual void RecvResourceStatusUpdate (ResourceStatusUpdateParams params);
	  /**
	   * Receive resource status Request function
	   * \param params the receive resource status Request
	   */
	  virtual void RecvResourceStatusRequest (ResourceStatusRequestParams params);
	  /**
	   * Receive resource status Response function
	   * \param params the receive resource status Response
	   */
	  virtual void RecvResourceStatusResponse (ResourceStatusResponseParams params);



	  /**
	   * Receive UE data function
	   * \param params the UE data parameters
	   */
	  virtual void RecvUeData (UeDataParams params);

	private:
	  EpcX2SpecificEpcX2SapUser ();
	  C* m_rrc; ///< owner class
};

template <class C>
EpcX2SpecificEpcX2SapUser<C>::EpcX2SpecificEpcX2SapUser (C* rrc)
  : m_rrc (rrc)
{
}

template <class C>
EpcX2SpecificEpcX2SapUser<C>::EpcX2SpecificEpcX2SapUser ()
{
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvHandoverRequest (HandoverRequestParams params)
{
  m_rrc->DoRecvHandoverRequest (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvHandoverRequestAck (HandoverRequestAckParams params)
{
  m_rrc->DoRecvHandoverRequestAck (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvHandoverPreparationFailure (HandoverPreparationFailureParams params)
{
  m_rrc->DoRecvHandoverPreparationFailure (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvSnStatusTransfer (SnStatusTransferParams params)
{
  m_rrc->DoRecvSnStatusTransfer (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvUeContextRelease (UeContextReleaseParams params)
{
  m_rrc->DoRecvUeContextRelease (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvLoadInformation (LoadInformationParams params)
{
  m_rrc->DoRecvLoadInformation (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvResourceStatusUpdate (ResourceStatusUpdateParams params)
{
  m_rrc->DoRecvResourceStatusUpdate (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvResourceStatusRequest (ResourceStatusRequestParams params)
{
  m_rrc->DoRecvResourceStatusRequest (params);
}

template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvResourceStatusResponse (ResourceStatusResponseParams params)
{
  m_rrc->DoRecvResourceStatusResponse (params);
}


template <class C>
void
EpcX2SpecificEpcX2SapUser<C>::RecvUeData (UeDataParams params)
{
  m_rrc->DoRecvUeData (params);
}

} // namespace ns3

#endif // EPC_X2_SAP_H
