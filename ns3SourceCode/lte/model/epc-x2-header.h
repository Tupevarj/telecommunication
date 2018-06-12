/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
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

#ifndef EPC_X2_HEADER_H
#define EPC_X2_HEADER_H

#include "ns3/epc-x2-sap.h"
#include "ns3/header.h"

#include <vector>


namespace ns3 {


class EpcX2Header : public Header
{
public:
  EpcX2Header ();
  virtual ~EpcX2Header ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint8_t GetMessageType () const;
  void SetMessageType (uint8_t messageType);

  uint8_t GetProcedureCode () const;
  void SetProcedureCode (uint8_t procedureCode);

  void SetLengthOfIes (uint32_t lengthOfIes);
  void SetNumberOfIes (uint32_t numberOfIes);


  enum ProcedureCode_t {
    HandoverPreparation     = 0,
    LoadIndication          = 2,
    SnStatusTransfer        = 4,
    UeContextRelease        = 5,
	ResourceStatusReportingInitiation = 9,
    ResourceStatusReporting = 10,

  };

  enum TypeOfMessage_t {
    InitiatingMessage       = 0,
    SuccessfulOutcome       = 1,
    UnsuccessfulOutcome     = 2
  };

private:
  uint8_t m_messageType;
  uint8_t m_procedureCode;

  uint32_t m_lengthOfIes;
  uint32_t m_numberOfIes;
};


class EpcX2HandoverRequestHeader : public Header
{
public:
  EpcX2HandoverRequestHeader ();
  virtual ~EpcX2HandoverRequestHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetOldEnbUeX2apId () const;
  void SetOldEnbUeX2apId (uint16_t x2apId);

  uint16_t GetCause () const;
  void SetCause (uint16_t cause);

  uint16_t GetTargetCellId () const;
  void SetTargetCellId (uint16_t targetCellId);

  uint32_t GetMmeUeS1apId () const;
  void SetMmeUeS1apId (uint32_t mmeUeS1apId);

  std::vector <EpcX2Sap::ErabToBeSetupItem> GetBearers () const;
  void SetBearers (std::vector <EpcX2Sap::ErabToBeSetupItem> bearers);

  uint64_t GetUeAggregateMaxBitRateDownlink () const;
  void SetUeAggregateMaxBitRateDownlink (uint64_t bitRate);

  uint64_t GetUeAggregateMaxBitRateUplink () const;
  void SetUeAggregateMaxBitRateUplink (uint64_t bitRate);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_oldEnbUeX2apId;
  uint16_t          m_cause;
  uint16_t          m_targetCellId;
  uint32_t          m_mmeUeS1apId;
  uint64_t          m_ueAggregateMaxBitRateDownlink;
  uint64_t          m_ueAggregateMaxBitRateUplink;
  std::vector <EpcX2Sap::ErabToBeSetupItem> m_erabsToBeSetupList;
};


class EpcX2HandoverRequestAckHeader : public Header
{
public:
  EpcX2HandoverRequestAckHeader ();
  virtual ~EpcX2HandoverRequestAckHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetOldEnbUeX2apId () const;
  void SetOldEnbUeX2apId (uint16_t x2apId);

  uint16_t GetNewEnbUeX2apId () const;
  void SetNewEnbUeX2apId (uint16_t x2apId);

  std::vector <EpcX2Sap::ErabAdmittedItem> GetAdmittedBearers () const;
  void SetAdmittedBearers (std::vector <EpcX2Sap::ErabAdmittedItem> bearers);

  std::vector <EpcX2Sap::ErabNotAdmittedItem> GetNotAdmittedBearers () const;
  void SetNotAdmittedBearers (std::vector <EpcX2Sap::ErabNotAdmittedItem> bearers);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_oldEnbUeX2apId;
  uint16_t          m_newEnbUeX2apId;
  std::vector <EpcX2Sap::ErabAdmittedItem>     m_erabsAdmittedList;
  std::vector <EpcX2Sap::ErabNotAdmittedItem>  m_erabsNotAdmittedList;
};


class EpcX2HandoverPreparationFailureHeader : public Header
{
public:
  EpcX2HandoverPreparationFailureHeader ();
  virtual ~EpcX2HandoverPreparationFailureHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetOldEnbUeX2apId () const;
  void SetOldEnbUeX2apId (uint16_t x2apId);

  uint16_t GetCause () const;
  void SetCause (uint16_t cause);

  uint16_t GetCriticalityDiagnostics () const;
  void SetCriticalityDiagnostics (uint16_t criticalityDiagnostics);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_oldEnbUeX2apId;
  uint16_t          m_cause;
  uint16_t          m_criticalityDiagnostics;
};


class EpcX2SnStatusTransferHeader : public Header
{
public:
  EpcX2SnStatusTransferHeader ();
  virtual ~EpcX2SnStatusTransferHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetOldEnbUeX2apId () const;
  void SetOldEnbUeX2apId (uint16_t x2apId);

  uint16_t GetNewEnbUeX2apId () const;
  void SetNewEnbUeX2apId (uint16_t x2apId);

  std::vector <EpcX2Sap::ErabsSubjectToStatusTransferItem> GetErabsSubjectToStatusTransferList () const;
  void SetErabsSubjectToStatusTransferList (std::vector <EpcX2Sap::ErabsSubjectToStatusTransferItem> erabs);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_oldEnbUeX2apId;
  uint16_t          m_newEnbUeX2apId;
  std::vector <EpcX2Sap::ErabsSubjectToStatusTransferItem> m_erabsSubjectToStatusTransferList;
};


class EpcX2UeContextReleaseHeader : public Header
{
public:
  EpcX2UeContextReleaseHeader ();
  virtual ~EpcX2UeContextReleaseHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetOldEnbUeX2apId () const;
  void SetOldEnbUeX2apId (uint16_t x2apId);

  uint16_t GetNewEnbUeX2apId () const;
  void SetNewEnbUeX2apId (uint16_t x2apId);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_oldEnbUeX2apId;
  uint16_t          m_newEnbUeX2apId;
};


class EpcX2LoadInformationHeader : public Header
{
public:
  EpcX2LoadInformationHeader ();
  virtual ~EpcX2LoadInformationHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  std::vector <EpcX2Sap::CellInformationItem> GetCellInformationList () const;
  void SetCellInformationList (std::vector <EpcX2Sap::CellInformationItem> cellInformationList);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  std::vector <EpcX2Sap::CellInformationItem> m_cellInformationList;
};


class EpcX2ResourceStatusUpdateHeader : public Header
{
public:
  EpcX2ResourceStatusUpdateHeader ();
  virtual ~EpcX2ResourceStatusUpdateHeader ();

  static TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetEnb1MeasurementId () const;
  void SetEnb1MeasurementId (uint16_t enb1MeasurementId);

  uint16_t GetEnb2MeasurementId () const;
  void SetEnb2MeasurementId (uint16_t enb2MeasurementId);

  uint16_t GetSourceEnbId () const;
  void SetSourceEnbId (uint16_t sourceEnbId);

  uint16_t GetTargetEnbId () const;
   void SetTargetEnbId (uint16_t targetEnbId);

  std::vector<EpcX2Sap::CellMeasurementResultItem> GetCellMeasurementResultList () const;
  void SetCellMeasurementResultList (std::vector<EpcX2Sap::CellMeasurementResultItem> cellMeasurementResultList);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t 			m_targetEnbId;
  uint16_t          m_sourceEnbId;

  uint16_t          m_enb1MeasurementId;
  uint16_t          m_enb2MeasurementId;
  std::vector<EpcX2Sap::CellMeasurementResultItem> m_cellMeasurementResultList;
};
/**
 * RESOURCE STATUS REQUEST MESSAGE
 * To be Modified
 */
class EpcX2ResourceStatusRequestHeader : public Header
{
public:
  EpcX2ResourceStatusRequestHeader ();
  virtual ~EpcX2ResourceStatusRequestHeader ();

  static  TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetEnb1MeasurementId () const;
  void SetEnb1MeasurementId (uint16_t enb1MeasurementId);

  uint16_t GetEnb2MeasurementId () const;
  void SetEnb2MeasurementId (uint16_t enb2MeasurementId);

  uint8_t GetRegistrationRequest () const;
  void SetRegistrationRequest (uint8_t regReq);

  std::bitset<32> GetReportCharacteristics () const;
  void SetReportCharacteristics (std::bitset<32>  reportCharacteristics);

  //std::vector<EpcX2Sap::CellId> GetTargetCellId() const;
  //void SetTargetCellId (std::vector<EpcX2Sap::CellId> cellToReportId);

  std::vector<uint16_t> GetTargetEnbId() const;
  void SetTargetEnbId ( std::vector<uint16_t> enbToReportId);

  uint16_t GetSourceEnbId () const;
  void SetSourceEnbId (uint16_t sourceEnbId);

  uint8_t GetPartialSuccessIndicator () const;
  void SetPartialSuccessIndicator (uint8_t PSI);

  uint8_t GetReportingPeriodicity () const;
  void SetReportingPeriodicity (uint8_t reportingPeriodicity);

  uint8_t GetPeriodicityRSRPMeasurementReport () const;
  void SetPeriodicityRSRPMeasurementReport (uint8_t periodicityRSRP);

  uint8_t GetPeriodicityCSIReport () const;
  void SetPeriodicityCSIReport (uint8_t periodicityCSI);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint8_t           m_messageType = 10; ///< ResourceStatusReportingInitiation
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;



  uint16_t          m_enb1MeasurementId =0;
  uint16_t          m_enb2MeasurementId =0 ;

  uint8_t			m_regReq = 0;

  std::bitset<32>    m_reportCharacteristics;

  uint16_t			m_sourceEnbId =0;

  std::vector<uint16_t>		 	m_targetEnbId ; //

  uint8_t			m_partialSuccessIndicator =0;
  uint8_t           m_reportingPeriodicity =0;
  uint8_t           m_periodicityRSRP =0;
  uint8_t           m_periodicityCSI =0;
};

/** MY************
 * RESOURCE STATUS RESPONSE MESSAGE
 * To be Modified
 */
class EpcX2ResourceStatusResponseHeader : public Header
{
public:
  EpcX2ResourceStatusResponseHeader ();
  virtual ~EpcX2ResourceStatusResponseHeader ();

  static  TypeId GetTypeId (void);
  virtual TypeId GetInstanceTypeId (void) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);
  virtual void Print (std::ostream &os) const;


  uint16_t GetEnb1MeasurementId () const;
  void SetEnb1MeasurementId (uint16_t enb1MeasurementId);

  uint16_t GetEnb2MeasurementId () const;
  void SetEnb2MeasurementId (uint16_t enb2MeasurementId);

  uint16_t GetTargetEnbId() const;
  void SetTargetEnbId (uint16_t targetCellId);

  uint16_t GetSourceEnbId () const;
  void SetSourceEnbId (uint16_t sourceEnbId);


  std::vector<EpcX2Sap::MeasurementInitiationResultItem> GetMeasurementInitiationResult () const;
  void SetMeasurementInitiationResult(std::vector<EpcX2Sap::MeasurementInitiationResultItem> measurementInitiationResultList);

  // uint8_t GetCause() const;
  // void SetCause(uint8_t cause);

 // std::bitset<32> GetMeasurementFailedReportCharacteristics () const;
 // void SetMeasurementFailedReportCharacteristics (std::bitset<32>  measurementFailedReportCharacteristics);

  uint32_t GetLengthOfIes () const;
  uint32_t GetNumberOfIes () const;

private:
  uint8_t           m_messageType = 10; ///< ResourceStatusReportingInitiation
  uint32_t          m_numberOfIes;
  uint32_t          m_headerLength;

  uint16_t          m_enb1MeasurementId;
  uint16_t          m_enb2MeasurementId;

  uint16_t			m_sourceEnbId;

  uint16_t			m_targetEnbId;

  std::vector<EpcX2Sap::MeasurementInitiationResultItem>  m_measurementInitiationResultList;

};



} // namespace ns3

#endif // EPC_X2_HEADER_H
