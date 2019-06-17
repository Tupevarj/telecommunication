/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2011 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
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
 * Author: Jaume Nin <jnin@cttc.es>
 */

#include "phy-stats-calculator.h"
#include "ns3/string.h"
#include <ns3/simulator.h>
#include <ns3/log.h>

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("PhyStatsCalculator");

NS_OBJECT_ENSURE_REGISTERED (PhyStatsCalculator);

PhyStatsCalculator::PhyStatsCalculator ()
  :  m_RsrpSinrFirstWrite (true),
    m_UeSinrFirstWrite (true),
    m_InterferenceFirstWrite (true)
{
  NS_LOG_FUNCTION (this);

}

PhyStatsCalculator::~PhyStatsCalculator ()
{
  NS_LOG_FUNCTION (this);
}

TypeId
PhyStatsCalculator::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::PhyStatsCalculator")
    .SetParent<LteStatsCalculator> ()
    .SetGroupName("Lte")
    .AddConstructor<PhyStatsCalculator> ()
    .AddAttribute ("DlRsrpSinrFilename",
                   "Name of the file where the RSRP/SINR statistics will be saved.",
                   StringValue ("DlRsrpSinrStats.txt"),
                   MakeStringAccessor (&PhyStatsCalculator::SetCurrentCellRsrpSinrFilename),
                   MakeStringChecker ())
    .AddAttribute ("UlSinrFilename",
                   "Name of the file where the UE SINR statistics will be saved.",
                   StringValue ("UlSinrStats.txt"),
                   MakeStringAccessor (&PhyStatsCalculator::SetUeSinrFilename),
                   MakeStringChecker ())
    .AddAttribute ("UlInterferenceFilename",
                   "Name of the file where the interference statistics will be saved.",
                   StringValue ("UlInterferenceStats.txt"),
                   MakeStringAccessor (&PhyStatsCalculator::SetInterferenceFilename),
                   MakeStringChecker ())
	.AddTraceSource ("SinrUeTrace",
			"Trace fired, when SINR calculated",
			 MakeTraceSourceAccessor (&PhyStatsCalculator::m_SinrTrace),
			"ns3::PhyStatsCalculator::SinrCallback")
	.AddTraceSource ("SinrEnbTrace",
					"Trace fired, when SINR calculated",
					 MakeTraceSourceAccessor (&PhyStatsCalculator::m_SinrEnbTrace),
					"ns3::PhyStatsCalculator::SinrEnbCallback")
  ;
  return tid;
}

void
PhyStatsCalculator::SetCurrentCellRsrpSinrFilename (std::string filename)
{
  m_RsrpSinrFilename = filename;
}

std::string
PhyStatsCalculator::GetCurrentCellRsrpSinrFilename (void)
{
  return m_RsrpSinrFilename;
}

void
PhyStatsCalculator::SetUeSinrFilename (std::string filename)
{
  m_ueSinrFilename = filename;
}

std::string
PhyStatsCalculator::GetUeSinrFilename (void)
{
  return m_ueSinrFilename;
}

void
PhyStatsCalculator::SetInterferenceFilename (std::string filename)
{
  m_interferenceFilename = filename;
}

std::string
PhyStatsCalculator::GetInterferenceFilename (void)
{
  return m_interferenceFilename;
}



void
PhyStatsCalculator::ReportCurrentCellRsrpSinr (uint16_t cellId, uint64_t imsi, uint16_t rnti,
                                               double rsrp, double sinr)
{
	//////////////////////////////////////////////
	// m_KpiTrace(imsi, cellId, rsrp, sinr);
	//////////////////////////////////////////////


  NS_LOG_FUNCTION (this << cellId <<  imsi << rnti  << rsrp << sinr);
  NS_LOG_INFO ("Write RSRP/SINR Phy Stats in " << GetCurrentCellRsrpSinrFilename ().c_str ());

  std::ofstream outFile;
  if ( m_RsrpSinrFirstWrite == true )
    {
      outFile.open (GetCurrentCellRsrpSinrFilename ().c_str ());
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetCurrentCellRsrpSinrFilename ().c_str ());
          return;
        }
      m_RsrpSinrFirstWrite = false;
      outFile << "% time\tcellId\tIMSI\tRNTI\trsrp\tsinr";
      outFile << std::endl;
    }
  else
    {
      outFile.open (GetCurrentCellRsrpSinrFilename ().c_str (),  std::ios_base::app);
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetCurrentCellRsrpSinrFilename ().c_str ());
          return;
        }
    }

  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//  int time = Simulator::Now().GetSeconds() * 1000;

//  if(time % 200 == 0)
//  {
	  m_SinrEnbTrace((Simulator::Now().GetSeconds() * 10)/10.0, imsi, cellId, 10.0 * log10(sinr));
//  }
  outFile << Simulator::Now ().GetNanoSeconds () / (double) 1e9 << ",";
	  outFile << cellId << ",";
	  outFile << imsi << ",";
	  outFile << rnti << ",";
	  outFile << 10.0 * log10(rsrp)<< ",";
//	  outFile << rsrp << "\t";
	  outFile << 10.0 * log10(sinr) << std::endl;
//  }
  outFile.close ();


  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
}

void
PhyStatsCalculator::ReportUeSinr (uint16_t cellId, uint64_t imsi, uint16_t rnti,  double sinrLinear)
{
  NS_LOG_FUNCTION (this << cellId <<  imsi << rnti  << sinrLinear);
  NS_LOG_INFO ("Write SINR Linear Phy Stats in " << GetUeSinrFilename ().c_str ());

  std::ofstream outFile;
  if ( m_UeSinrFirstWrite == true )
    {
      outFile.open (GetUeSinrFilename ().c_str ());
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetUeSinrFilename ().c_str ());
          return;
        }
      m_UeSinrFirstWrite = false;
      outFile << "% time\tcellId\tIMSI\tRNTI\tsinrLinear";
      outFile << std::endl;
    }
  else
    {
      outFile.open (GetUeSinrFilename ().c_str (),  std::ios_base::app);
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetUeSinrFilename ().c_str ());
          return;
        }
    }

  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // if (time % 200 < 2) saadann 400 800 1200...

//  int time = Simulator::Now().GetSeconds() * 1000;  // 0.641 -> 641 s    80  600 / 80
//
//  // 0.08 s
//
//  if(time % 200 == 2 || time % 200 == 41)
//  {
	  m_SinrTrace((Simulator::Now().GetSeconds() * 10)/10.0, imsi, cellId, 10.0 * log10(sinrLinear));
//  }
	  outFile << Simulator::Now ().GetNanoSeconds () / (double) 1e9 << ",";
	  outFile << cellId << ",";
	  outFile << imsi << ",";
	  outFile << rnti << ",";
	  outFile << 10.0 * log10(sinrLinear) << std::endl;
	  outFile.close ();
//  }
  outFile.close ();
}

void
PhyStatsCalculator::ReportInterference (uint16_t cellId, Ptr<SpectrumValue> interference)
{
  NS_LOG_FUNCTION (this << cellId <<  interference);
  NS_LOG_INFO ("Write Interference Phy Stats in " << GetInterferenceFilename ().c_str ());

  std::ofstream outFile;
  if ( m_InterferenceFirstWrite == true )
    {
      outFile.open (GetInterferenceFilename ().c_str ());
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetInterferenceFilename ().c_str ());
          return;
        }
      m_InterferenceFirstWrite = false;
      outFile << "% time\tcellId\tInterference";
      outFile << std::endl;
    }
  else
    {
      outFile.open (GetInterferenceFilename ().c_str (),  std::ios_base::app);
      if (!outFile.is_open ())
        {
          NS_LOG_ERROR ("Can't open file " << GetInterferenceFilename ().c_str ());
          return;
        }
    }

  outFile << Simulator::Now ().GetNanoSeconds () / (double) 1e9 << "\t";
  outFile << cellId << "\t";
  outFile << *interference;
  outFile.close ();
}


void
PhyStatsCalculator::ReportCurrentCellRsrpSinrCallback (Ptr<PhyStatsCalculator> phyStats,
                      std::string path, uint16_t cellId, uint16_t rnti,
                      double rsrp, double sinr)
{
  NS_LOG_FUNCTION (phyStats << path);
  uint64_t imsi = 0;
  std::string pathUePhy  = path.substr (0, path.find ("/ReportCurrentCellRsrpSinr"));
  if (phyStats->ExistsImsiPath (pathUePhy) == true)
    {
      imsi = phyStats->GetImsiPath (pathUePhy);
    }
  else
    {
      imsi = FindImsiFromUePhy (pathUePhy);
      phyStats->SetImsiPath (pathUePhy, imsi);
    }

  phyStats->ReportCurrentCellRsrpSinr (cellId, imsi, rnti, rsrp,sinr);
}


void
PhyStatsCalculator::ReportUeSinr (Ptr<PhyStatsCalculator> phyStats, std::string path,
              uint16_t cellId, uint16_t rnti, double sinrLinear)
{
  NS_LOG_FUNCTION (phyStats << path);

  uint64_t imsi = 0;
  std::ostringstream pathAndRnti;
  pathAndRnti << path << "/" << rnti;
  std::string pathEnbMac  = path.substr (0, path.find ("LteEnbPhy/ReportUeSinr"));
  pathEnbMac += "LteEnbMac/DlScheduling";
  if (phyStats->ExistsImsiPath (pathAndRnti.str ()) == true)
    {
      imsi = phyStats->GetImsiPath (pathAndRnti.str ());
    }
  else
    {
      imsi = FindImsiFromEnbMac (pathEnbMac, rnti);
      phyStats->SetImsiPath (pathAndRnti.str (), imsi);
    }

  phyStats->ReportUeSinr (cellId, imsi, rnti, sinrLinear);
}

void
PhyStatsCalculator::ReportInterference (Ptr<PhyStatsCalculator> phyStats, std::string path,
                    uint16_t cellId, Ptr<SpectrumValue> interference)
{
  NS_LOG_FUNCTION (phyStats << path);
  phyStats->ReportInterference (cellId, interference);
}


} // namespace ns3
