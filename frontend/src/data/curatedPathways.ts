/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { PathwayDetail } from '../types';

export const curatedPathways: Record<string, Record<string, PathwayDetail>> = {
  // Key format: "NOC_CODE" : { "PROVINCE_CODE": PathwayDetail }
  // Provinces: "ON" (Ontario), "BC" (British Columbia), "AB" (Alberta), "QC" (Quebec)
  
  // 1. Registered Nursing (NOC 31301)
  "31301": {
    "ON": {
      nocCode: "31301",
      title: "Registered Nurse (RN)",
      province: "Ontario",
      regulatoryBody: "College of Nurses of Ontario (CNO)",
      regulatorWebsite: "https://www.cno.org",
      typicalTime: "12 - 24 months",
      typicalCost: "$1,500 - $3,500 CAD (Assessment & Exams)",
      fundingOptions: [
        "Windmill Microlending: Up to $15,000 in low-interest loans for refugee licensing costs.",
        "Ontario Bridging Participant Assistance Program (OBPAP): Up to $5,000 in bursaries.",
        "Supervised Practice Experience Partnership (SPEP): Paid practice program by CNO/Health Force Ontario."
      ],
      childcareSupport: "Ontario Child Care Fee Subsidy: Apply directly via local municipality. Can cover up to 100% of licensed childcare costs during bridging studies and exams.",
      steps: [
        {
          id: 1,
          title: "Address Missing Documents (Displacement Route)",
          description: "If academic documents are unavailable because you fled your country, notify the CNO directly. Under CNO's 'Special Circumstances Policy', they allow retroactive alternative assessments. First, complete the online application on the CNO portal, select 'Cannot provide documents due to conflict/displacement', and fill out the Statutory Declaration of educational experience (Form B) with any secondary supporting evidence.",
          status: "info",
          statusText: "Alternative proof path available"
        },
        {
          id: 2,
          title: "National Nursing Assessment Service (NNAS) Report",
          description: "Submit matching credentials to NNAS. If documents are missing, NNAS can issue a 'Document Advisory' which forwards your profile to CNO for active alternative credential reviews, bypassing the normal NNAS block.",
          actionLabel: "Access NNAS Portal",
          actionUrl: "https://www.nnas.ca",
          status: "pending",
          statusText: "Pre-assessment"
        },
        {
          id: 3,
          title: "Language Competency Verification",
          description: "Demonstrate professional communication in English or French (IELTS level 7+, CELBAN, or French TEF). Refugee newcomers can access free language training for nursing (Language Instruction for Newcomers (LINC)) through settlement agencies.",
          status: "ready",
          statusText: "Free LINC training matches"
        },
        {
          id: 4,
          title: "Complete Bridging Studies or Supervised Practice",
          description: "Complete localized bridging courses (e.g., George Brown or CARE Centre for Internationally Educated Nurses). Or apply to 'SPEP' to earn your clinical horas through registered paid nursing work in ON hospitals.",
          actionLabel: "CARE Centre for Nurses",
          actionUrl: "https://www.care4nurses.org",
          status: "ready",
          statusText: "Paid training option"
        },
        {
          id: 5,
          title: "Pass the NCLEX-RN Examination",
          description: "Register and pass the National Council Licensure Examination for Registered Nurses. Funding from Windmill can fully cover prep courses and exam attempts.",
          status: "pending",
          statusText: "Licensure exam"
        }
      ],
      nameDiscrepancyGuide: "Name changes due to gender transition or displacement-driven spelling differences across national passports can be verified with CNO using a single statutory declaration accompanied by refugee board letters or a provincial name change certificate. CNO will update all files under your preferred name."
    },
    "BC": {
      nocCode: "31301",
      title: "Registered Nurse (RN)",
      province: "British Columbia",
      regulatoryBody: "British Columbia College of Nurses and Midwives (BCCNM)",
      regulatorWebsite: "https://www.bccnm.ca",
      typicalTime: "12 - 18 months",
      typicalCost: "$2,000 - $4,000 CAD",
      fundingOptions: [
        "Career Paths for Skilled Immigrants: BC funded program providing up to $4,000 for licensing exam/training fees.",
        "Health Match BC Bursaries: Government bursaries covering up to 100% of assessment costs dynamically.",
        "Windmill Microlending: Low-interest newcomer credits."
      ],
      childcareSupport: "ChildCareBC Affordable Child Care Benefit: BC government subsidy of up to $1,250 per month per child. Available for nursing exam preparation and bridging class schedules.",
      steps: [
        {
          id: 1,
          title: "Initiate BCCNM Assessment with Refugee Status",
          description: "BCCNM has an interactive assessment pathway for refugees with missing records. Contact BCCNM's Internationally Educated Nurse (IEN) office specifically to request their 'Undocumented Professional Experience' review protocol, where they accept work validation letters from past colleagues in lieu of official university seal scripts.",
          status: "info",
          statusText: "Undocumented protocol active"
        },
        {
          id: 2,
          title: "Nursing Community Assessment Service (NCAS)",
          description: "Take the NCAS computer-based assessment and simulation-based clinical assessment to evaluate current skills. This highlights competency gaps without requiring rigid syllabus transcripts.",
          actionLabel: "Visit NCAS Portal",
          actionUrl: "https://www.ncasbc.ca",
          status: "pending",
          statusText: "Practical skills review"
        },
        {
          id: 3,
          title: "Pass the NCLEX-RN and Obtain License",
          description: "Upon obtaining your NCAS results, BCCNM will direct you to write the standard licensing exam (NCLEX) or take short, free bridging modules.",
          status: "pending",
          statusText: "Final licensing exam"
        }
      ],
      nameDiscrepancyGuide: "BCCNM provides high-priority support for trans and non-binary health workers. Inconsistencies on official foreign school documents are approved through a direct statutory submission with BCCNM Registrar without public records exposure."
    }
  },

  // 2. Early Childhood Educators (NOC 42202)
  "42202": {
    "ON": {
      nocCode: "42202",
      title: "Early Childhood Educator (ECE)",
      province: "Ontario",
      regulatoryBody: "College of Early Childhood Educators (CECE)",
      regulatorWebsite: "https://www.college-ece.ca",
      typicalTime: "3 - 8 months",
      typicalCost: "$300 - $800 CAD",
      fundingOptions: [
        "Ontario Bridging Participant Assistance Program (OBPAP)",
        "ECE Qualifications Upgrade Program (QUP): Paid tuition grants and training allowances of up to $2,000.",
        "Windmill Microlending: Small-scale personal licensing loans."
      ],
      childcareSupport: "Ontario Municipality Child Care Subsidy: Full coverage for children while ECE candidates are completing fast-track credential licensing or night courses.",
      steps: [
        {
          id: 1,
          title: "Check Equivalency Without Papers",
          description: "If you fled without your official diploma, the CECE registration department handles emergency displacement folders individually. Compile any secondary papers (old digital photos of diplomas, transcript lists, text messages, employer contacts). CECE works with World Education Services (WES) Gateway Program to assess partial qualifications.",
          actionLabel: "Learn about WES Gateway (Refugees)",
          actionUrl: "https://www.wes.org/ca/gateway-program-refugees/",
          status: "info",
          statusText: "WES Gateway eligible"
        },
        {
          id: 2,
          title: "WES Credential evaluation & Equivalence Match",
          description: "Get a custom evaluation report. If complete information is missing, WES Gateway validates refugee studies based on self-reports and verified subject testing.",
          status: "ready",
          statusText: "Refugee-accessible assessment"
        },
        {
          id: 3,
          title: "Language and Membership Registration",
          description: "Submit IELTS/TEF/LINC level results matching direct workplace proficiency requirements. Register directly as a Registered Early Childhood Educator (RECE) in Ontario.",
          status: "pending",
          statusText: "Final registration steps"
        }
      ]
    },
    "BC": {
      nocCode: "42202",
      title: "Early Childhood Educator (ECE)",
      province: "British Columbia",
      regulatoryBody: "BC ECE Registry",
      regulatorWebsite: "https://www2.gov.bc.ca/gov/content/education-training/early-learning/teach/ece",
      typicalTime: "2 - 6 months",
      typicalCost: "$150 - $400 CAD",
      fundingOptions: [
        "ECE Education Support Fund: Bursaries up to $5,000 per semester for students or internationally trained educators upgrading BC skills.",
        "WorkBC Skills Training Grants"
      ],
      childcareSupport: "BC Affordable Child Care Subsidy: Prioritized child spaces and tuition grants for parents entering educational disciplines.",
      steps: [
        {
          id: 1,
          title: "Alternative Document Route for Refugees",
          description: "If academic credentials are lost, the BC Ministry of Education and ECE Registry accept a comprehensive statutory declaration and secondary employer references. Email the ECE Registry directly detailing your displacement and requesting 'Equivalent Document Assessment Waiver' conditions.",
          status: "info",
          statusText: "Waiver process available"
        },
        {
          id: 2,
          title: "Evaluate Experience Points and Register",
          description: "Once background is reviewed or WES Gateway report is submitted, BC will match your background to an assistant-level or full educator certificate.",
          status: "ready",
          statusText: "Direct certification"
        }
      ]
    }
  },

  // 3. Civil Engineers (NOC 21300)
  "21300": {
    "ON": {
      nocCode: "21300",
      title: "Civil Engineer",
      province: "Ontario",
      regulatoryBody: "Professional Engineers Ontario (PEO)",
      regulatorWebsite: "https://www.peo.on.ca",
      typicalTime: "6 - 18 months (PEO changed rules to drop Canadian experience requirement!)",
      typicalCost: "$800 - $2,500 CAD",
      fundingOptions: [
        "Engineering Access Bridging Programs: Funded by ON govt, helps prepare for local exams.",
        "Windmill Microlending: Low-interest loans up to $15,000."
      ],
      childcareSupport: "Ontario Child Care Subsidies via local Municipalities: Keeps children cared for while studying for the Professional Practice Exam (PPE).",
      steps: [
        {
          id: 1,
          title: "Note: PEO No Longer Requires Canadian Experience!",
          description: "As of May 2, 2023, PEO has removed the rigid 12-month Canadian work experience licensing requirement. You can now qualify solely on international engineering accomplishments, making licensing significantly faster for refugee newcomers.",
          status: "info",
          statusText: "Path normalized"
        },
        {
          id: 2,
          title: "WES Gateway Document Assessment",
          description: "If official transcripts are unreachable, utilize the World Education Services (WES) Gateway Program to verify your engineering credentials based on curriculum reviews and verified tests.",
          actionLabel: "Access WES Gateway Details",
          actionUrl: "https://www.wes.org/ca/gateway-program-refugees/",
          status: "ready",
          statusText: "Refugee-safe evaluation"
        },
        {
          id: 3,
          title: "National Professional Practice Exam (NPPE)",
          description: "Study for and pass the computer-based NPPE, which tests knowledge of Canadian engineering law, professional ethics, and liability regulations.",
          status: "pending",
          statusText: "Required licensing exam"
        }
      ]
    },
    "BC": {
      nocCode: "21300",
      title: "Civil Engineer",
      province: "British Columbia",
      regulatoryBody: "Engineers and Geoscientists British Columbia (EGBC)",
      regulatorWebsite: "https://www.egbc.ca",
      typicalTime: "8 - 20 months",
      typicalCost: "$1,000 - $3,000 CAD",
      fundingOptions: [
        "Career Paths for Skilled Immigrants: Provides funding for EGBC assessments and free training modules.",
        "Windmill Newcomer Engineering Licensure Loans."
      ],
      childcareSupport: "ChildCareBC Affordable Benefit: Monthly subsidies to support you during study hours for the NPPE.",
      steps: [
        {
          id: 1,
          title: "Alternative Document Pathway with EGBC",
          description: "EGBC has an active statutory review process for refugees who cannot procure official engineering transcripts. Reach out directly to EGBC's registration coordinator to file an 'Academic Document Waiver' along with a statutory declaration of your university's program syllabus.",
          status: "info",
          statusText: "Academic waiver route active"
        },
        {
          id: 2,
          title: "Competency Assessment Framework",
          description: "Rather than validating textbooks, EGBC lets you prove engineering qualifications online via a detailed Competency-Based Assessment (CBA) system, matching clinical engineering tasks from your past international projects.",
          status: "ready",
          statusText: "Competency based"
        },
        {
          id: 3,
          title: "Write Professional Practice Exam (NPPE)",
          description: "Pass the Canadian professional standards exam. EGBC provides study syllabus resources online.",
          status: "pending",
          statusText: "Final engineering exam"
        }
      ]
    }
  },

  // 4. Primary/Secondary School Teachers (NOC 41201 / 41221)
  "41201": {
    "ON": {
      nocCode: "41201",
      title: "School Teacher",
      province: "Ontario",
      regulatoryBody: "Ontario College of Teachers (OCT)",
      regulatorWebsite: "https://www.oct.ca",
      typicalTime: "12 - 24 months",
      typicalCost: "$500 - $1,500 CAD",
      fundingOptions: [
        "Ontario Bridging Program for Internationally Educated Teachers (administered by universities like York and OISE).",
        "Windmill Newcomer Funding."
      ],
      childcareSupport: "Ontario Child Care Subsidy: Directly supports family care during student teaching placements (which are full-time and unpaid).",
      steps: [
        {
          id: 1,
          title: "Request the OCT Refugee Protocol",
          description: "The Ontario College of Teachers maintains a dedicated program for educators displaced by war or humanitarian crises who don't have complete academic records. You can sign a Statutory Declaration (OCT Form Ref-1) outlining your teaching accomplishments, years of employment, and teaching college program courses.",
          status: "info",
          statusText: "Refugee protocol active"
        },
        {
          id: 2,
          title: "Language Fluency Assessment",
          description: "Teachers in Ontario must be fully fluent in English or French. Provide IELTS (7+ in reading, 8 in listening/speaking) or TEF. LINC (Language Instruction for Newcomers) provides free specialized terminology classes.",
          status: "ready",
          statusText: "Free language workshops"
        },
        {
          id: 3,
          title: "Bridging and Transitional Certificate",
          description: "OCT may issue a 'Transitional Certificate of Qualification', enabling you to teach as a paid supply teacher in Ontario public boards while completing any final pedagogical modules.",
          status: "info",
          statusText: "Earn while qualifying"
        }
      ],
      nameDiscrepancyGuide: "OCT accepts legal statutory declarations for transgender educators to update academic history columns without showing deadnames on public licensing registers."
    }
  }
};

// Simple helper to find nearest match from general database if not hardcoded
export function getPathwayWithFallback(nocCode: string, province: string, documentsAvailable: string, userQuery: string): PathwayDetail {
  const cleanProvince = province || "ON";
  const normalizedNoc = nocCode.trim();

  // If we have a curated pathway, return it
  if (curatedPathways[normalizedNoc] && curatedPathways[normalizedNoc][cleanProvince]) {
    const detailed = { ...curatedPathways[normalizedNoc][cleanProvince] };
    
    // Adapt step 1 to match documentsAvailable input dynamically
    if (documentsAvailable === 'none') {
      // Step 1 already covers undocumented, highlight it!
    } else {
      // Modify first step description if they have documents
      detailed.steps = detailed.steps.map(step => {
        if (step.id === 1) {
          return {
            ...step,
            title: "Prepare Your Academic Documentation",
            description: "Since you indicated you have documents available, gather your official transcripts and diplomas. Prepare certified English or French translations before submitting them to the regulatory body to fast-track your folder assessments.",
            statusText: "Documents check"
          };
        }
        return step;
      });
    }
    return detailed;
  }

  // Look if there's any other province for this NOC code, then adapt it
  if (curatedPathways[normalizedNoc]) {
    const fallbackProv = Object.keys(curatedPathways[normalizedNoc])[0];
    const original = curatedPathways[normalizedNoc][fallbackProv];
    
    // Safety matching helper escaping special characters [.*+?^${}()|[\]\\]
    const escapeRegExp = (str: string) => (str || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const escapedRegulator = escapeRegExp(original.regulatoryBody);
    const escapedProvince = escapeRegExp(original.province);
    const targetProvinceName = getProvinceFullName(cleanProvince);

    return {
      ...original,
      province: targetProvinceName,
      regulatoryBody: `Provincial Regulatory Body for ${original.title} (${cleanProvince})`,
      steps: original.steps.map(s => ({
        ...s,
        description: s.description
          .replace(new RegExp(escapedRegulator, 'g'), `Provincial Board (${cleanProvince})`)
          .replace(new RegExp(escapedProvince, 'g'), targetProvinceName)
      }))
    };
  }

  // Dynamic Fallback Generator for any unlisted NOC
  const defaultTitle = userQuery ? `Licensed Specialist (${normalizedNoc})` : `Profession (${normalizedNoc})`;
  const provinceName = getProvinceFullName(cleanProvince);
  const regulatoryBodyText = `Provincial Regulatory Authority of ${provinceName}`;

  return {
    nocCode: normalizedNoc,
    title: defaultTitle,
    province: provinceName,
    regulatoryBody: regulatoryBodyText,
    typicalTime: "6 - 18 months",
    typicalCost: "$500 - $2,000 CAD (variable)",
    fundingOptions: [
      "Windmill Microlending: Low-interest credential Loans up to $15,000 for refugee newcomers across Canada.",
      "Employment Insurance (EI) Skills Development benefits & provincial newcomer employment micro-grants."
    ],
    childcareSupport: `${provinceName} Child Care Benefits: Subsidized placements available to qualifying newcomer parents while undertaking professional bridging studies and exams.`,
    steps: [
      {
        id: 1,
        title: documentsAvailable === 'none' ? "Address Undocumented Experience" : "Compile Credentials",
        description: documentsAvailable === 'none'
          ? `Because you fled without papers, you can leverage Canada's assessment waiver paths. Submit a detailed statutory declaration of experience and educational syllabi directly to the ${regulatoryBodyText}. Modern regulatory bodies across Canada are legally mandated to offer an alternative verification route for refugees under displacement protocols.`
          : `Gather your verified transcripts, diploma certificates, and employment letters. Request certified translations to English or French to fast-track assessments by ${regulatoryBodyText}.`,
        status: "info",
        statusText: documentsAvailable === 'none' ? "Refugee path available" : "Document check"
      },
      {
        id: 2,
        title: "Credential Assessment & Verification",
        description: "Apply for a credential comparison report (such as World Education Services WES Gateway or typical evaluation panels) to map your foreign coursework equivalence to Canadian standards.",
        status: "pending",
        statusText: "Equivalency assessment"
      },
      {
        id: 3,
        title: "Language Proficiency Testing",
        description: "Submit certified test results (IELTS, CELPIP, or TEF) demonstrating communication benchmarks appropriate to the professional tasks of this discipline.",
        status: "ready",
        statusText: "Free settlement LINC training available"
      },
      {
        id: 4,
        title: "Write Professional Standards Exam & Register",
        description: `Apply for and write the professional practice code regulations examinations. Complete licensing registrations at ${regulatoryBodyText} for full certification.`,
        status: "pending",
        statusText: "Registration review"
      }
    ],
    nameDiscrepancyGuide: "Provincial human rights codes protect trans and non-binary professionals. Name spelling variations between historical degrees and current legal status can be harmonized by filing a sworn affidavit with the Registrar."
  };
}

function getProvinceFullName(code: string): string {
  const mapping: Record<string, string> = {
    "ON": "Ontario",
    "BC": "British Columbia",
    "AB": "Alberta",
    "QC": "Quebec",
    "MB": "Manitoba",
    "SK": "Saskatchewan",
    "NS": "Nova Scotia",
    "NB": "New Brunswick",
    "NL": "Newfoundland",
    "PE": "Prince Edward Island"
  };
  return mapping[code] || "Canada";
}
