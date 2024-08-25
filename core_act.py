def add_unspecify(dicc):
    for key in dicc:
        for core in dicc[key]:
            core["activities"].append(f"Unspecified {core['core_activity']}")

def create_dicc_color(dicc):
    new_dict_color={}

    for key in dicc:
        for aux_dict in dicc[key]:
            act = aux_dict["core_activity"]
            color = aux_dict["color"]
            new_dict_color[act] = color
            
    return new_dict_color

#Returns a dictionary where the key is the name of the core activity and the value is the list of corresponding subactivities
def create_dicc_subactivities(dicc):
    new_dicc_core = {}
    new_dicc_sub = {}
    for key in dicc:
        for aux_dicc in dicc[key]:
            core_activity = aux_dicc['core_activity']
            subactivities = aux_dicc['activities']
            new_dicc_core[core_activity] = subactivities
            new_dicc_sub = dict(new_dicc_sub, **{s: core_activity for s in subactivities})
    return new_dicc_core, new_dicc_sub

def load_activities():
    dicc_core = {
        "General": [{
            "core_activity": "Faculty plan/capacity group plan", 
            "color" : "#FFB6C1", 
            "activities": [
            "Setting out long-term policies for the chair, both in technical terms (research and education) as well as with regard to its social significance and added value (valorisation)",
            "Analysing the resources available (both internal and external) for research and education in terms of FTE for the coming academic year",
            "Reading trade journals, visiting conferences and maintaining relations with fellow researchers"
            ]
            },
            {
                "core_activity": "Management of education and research", 
                "color": "#FFD700",
                "activities": [
                    "Maintaining and developing relationships and contacts within the various scientific networks",
                    "Fostering national and international cooperation with other faculties, universities and other partners in society",
                    "Consulting with the Capacity Group Chairman on the progress of education and research within the chair and to take action or make suitable changes"
                ] 
            },
            {
                "core_activity": "Human Resources policy",
                "color": '#FFA07A',
                "activities": [
                    "Contributing to the recruitment and selection of employees",
                    "Conducting performance assessment interviews with employees of the chair",
                    "Development of talent and professionalisation of employees",
                    "Following a course for personal development",
                    "Coaching and supervision of employees of the chair",
                    "Sharing information from the various consultation bodies with the employees of the chair"
                ]
            },
            {
                "core_activity": "Organizational matters",
                "color": "#AFEEEE",
                "activities": [
                    "Requesting and assessing leave",
                    "Claiming and assessing expenses",
                    "Reporting sickness",
                    "Salary slip inspection",
                    "Requesting coaching/intervision/mentoring",
                    "Preparing and discussing official performance assessments",
                    "Solving / finding help for small issues"
                ]
            },
            {
                "core_activity": "Programme development",
                "color": "#98FB98",
                "activities": [
                    "Monitoring relevant national and international developments in their own field of education",
                    "Conducting analyses, or having analyses conducted, of educational needs in society and the learning needs of students",
                    "Ensuring the selection of relevant literature and teaching methodologies",
                    "Ensuring that relevant developments are translated into one or more course components and that these are submitted to the Programme Committee for approval",
                    "Ensuring the preparation of teaching materials, assignments, questions for exams and examinations"
                ]
            },
            {
                "core_activity":"Acquisition of contract teaching and research",
                "color": "#FF6347",
                "activities": [
                    "Initiating development of non-subsidised education",
                    "Exploring the external market for funding as well as the requirements of external potential partners or funders",
                    "Negotiating with external parties regarding the requirements for contract research and education and drafting and submitting proposals to external parties",
                    "Developing and maintaining contacts with leading researchers and research and education funders",
                    "Stimulating employees of the chair to apply for external funding",
                    "Acquiring grants and encouraging employees to apply for external funding",
                    "Contributing to the development of non-subsidised education",
                    "Identifying relevant developments and potential opportunities in the field of education and research" 
                ]
            },
            {
                "core_activity": "Accountability for contract teaching and research",
                "color":"#D8BFD8",
                "activities":[
                    "Reporting to the client regarding implementation and results",
                    "Discussing progress and reports thereof with those parties implementing contract teaching and research",
                    "Making appropriate changes to contract teaching and research if there are discrepancies regarding the contract requirements in terms of funding, duration, planning and objectives"

                ]
            },
            {
                "core_activity":"Advancing/communicating scientific knowledge and insight",
                "color":"#FFEBCD",
                "activities":[ 
                    "Creating and advancing networks aimed at the dissemination of knowledge and insight",
                    "Initiating national and international collaboration opportunities with other faculties, universities and other partners in society",
                    "Actively contributing to social debates",
                    "Encouraging and giving lectures",
                    "Encouraging and giving interviews for various media outlets",
                    "Exploring and responding to the needs for new research expressed by society"

                ]
            },
            {
                "core_activity": "Working groups and committees",
                "color":"#FFE4B5",
                "activities":[ 
                    "Preparing the topics to be discussed within the relevant working groups or committees",
                    "Participating in or leading the meetings of the committees and working groups",
                    "Elaborating certain issues and topics in preparation of a future meeting",
                    "Keeping the employees within the chair informed of the issues discussed within the working groups"
                ]
            },
            {
                "core_activity": "Contribution to the research group or lab",
                "color":"#FFD700",
                "activities":[ 
                    "Participating in group meetings",
                    "Organizing practical aspects for the group",
                    "Keeping members up-to-date with relevant information regarding organization, research or education"
                ]
            },
            {
                "core_activity": "Organization of (series of) events",
                "color":"#FFE4C4",
                "activities":[ 
                    "Proposing events",
                    "Organizing practical aspects of events",
                    "Communicating about events",
                    "Chairing events"
                ]
            }
        ],
        "General (extended)": [
            {
                "core_activity": "No work-related",
                "color":"#FFD4C7",
                "activities":[]
            },
            {
                "core_activity": "Communicating with others (Mail, Teams...)",
                "color":"#FF5733",
                "activities":[]
            },
            {
                "core_activity": "Personal productivity",
                "color":"#FFF333",
                "activities":[
                    "Planning daily/weekly work"
                ]
            }


        ],
                                                                                                            
        "Education": [
            {
                "core_activity": "Provision of education",
                "color":"#B0C4DE",
                "activities":[ 
                    "Ensuring the preparation and provision of assigned course components",
                    "Ensuring the evaluation and, where necessary, adjustment of assigned course components",
                    "Ensuring the integration of research results in education",
                    "Ensuring the application of the quality system",
                    "Coordinating with the Director of the teaching institute on the staffing for the provision of the assigned course components",
                    "Integrating research results into the curriculum",
                    "Preparing and providing teaching sessions for students, providing prospective students with information",
                    "Creating the right conditions for the learning process by applying didactic teaching methods",
                    "Supervising and coaching students during teaching sessions in the learning process",
                    "Supervising and assessing work placement and final projects and theses of students",
                    "Preparing practicals, tutorials and pre-structured lectures, etc.",
                    "Providing practicals, tutorials and pre-structured lectures, etc.",
                    "Co-authoring and assessing assignments and papers in a teaching context"
                ]
            },
            {
                "core_activity":"Student supervision",
                "color":"#FFDAB9",
                "activities":[ 
                    "Discussing possible assignments with students",
                    "Discussing the structure, provision and progress of the assignment with students",
                    "Assessing the students’ assignments and submitting the assessment to the Board of Examiners",
                    "Determining the integration of graduation subjects within the research plan with students",
                    "Providing input for the assessment of graduating students",
                    "Discussing the progress of research with students",
                    "Assisting with the correcting of theses, graduation projects and reports"
                    
                ]
            },
            {
                "core_activity":"PhD candidates",
                "color":"#DDA0DD",
                "activities":[ 
                    "Informing PhD candidates on possible doctoral thesis subjects",
                    "Hiring PhD candidates for doctoral research",
                    "Supervising and discussing the progress of the partial or completed research with PhD candidates",
                    "Assessing the thesis of the PhD candidate",
                    "Testing the training programmes set up by PhD candidates against the requirements of the policy on PhD candidates and the requirements of the National Graduate School if participation is taking place in this",
                    "Providing the supervisor with input for the assessment of PhD candidates",
                    "Supervising PhD candidates in the preparation and provision of a course component to be taught together and providing relevant"
                    
                ]
            },
            {
                "core_activity": "Education development",
                "color":"#E6E6FA",
                "activities":[ 
                    "Monitoring relevant national and international developments in their own field of education",
                    "Analysing the educational needs of society and students’ learning needs",
                    "Creating formats for new or adapting existing course components based on relevant developments in coordination with relevant colleagues",
                    "Selecting relevant literature and teaching methods",
                    "Creating or adapting teaching materials and assignments"
                    
                ]
            },
            {
                "core_activity": "Testing",
                "color":"#FFFAF0",
                "activities":[
                    "Creating formats for new or adapting existing exam questions based on relevant developments",
                    "Administering both oral and written exams",
                    "Assessing exams and giving marks",
                    "Drafting exam papers" 
                    
                ]
            },
            {
                "core_activity": "Education evaluation",
                "color":"#E0FFFF",
                "activities":[ 
                    "Evaluating and adjusting their course components where necessary",
                    "Drafting and implementing improvement proposals for their own course components and any related course components",
                    "Participating in internal working groups and discussions regarding education evaluation",
                    "Analysing the provision of course components with students and lecturers",
                    "Contributing to evaluation reports regarding the format and provision of the curriculum or components thereof",
                    "Collecting information for external education review committees",
                    "Providing information to external education review committees",
                    "Providing information to teaching assessment panels"
                    
                ]
            },
            {
                "core_activity": "Education coordination",
                "color":"#FFF8DC",
                "activities":[ 
                    "Encouraging the alignment of the development and execution of course components",
                    "Improving cohesion, both in terms of methodology and content, between course components",
                    "Assigning job assignments and giving instructions as well as monitoring the progress and quality of their execution by academic and teaching support staff",
                    "Cooperating in the recruitment, selection and assessment of teaching support staff",
                    "Communicating to students about the teaching material and assessment",
                    "Planning teaching activities",
                    "Aligning with other courses",
                    "Assessing student admission portfolios",
                    "Assessing scholarship applications",
                    "Assessing hardship appeals",
                    "Participating in educational marketing events",
                    "Updating programme website texts",
                    "Assessing suitability and quality of theses for thesis award",
                    "Realizing collegial course transferral"
                ]
            }
            

        ],
        "Research":[
            {
                "core_activity":"Research development",
                "color":"#F0FFF0",
                "activities":[ 
                    "Monitoring relevant national and international scientific developments in the chair's research field",
                    "Exploring and assessing the societal need for research and the opportunities for valorisation of that research",
                    "Creating initiatives for new research programme in consultation with relevant national and international colleagues (and external parties) based on consideration of the various developments (scientific content, societal needs, opportunities for valorisation)",
                    "Ensuring the translation of a research programme into research projects",
                    "Initiating a new research project in coordination with relevant national and international colleagues (and external parties) based on relevant developments (scientific content, needs of society, opportunities for valorisation)",
                    "Drafting a research plan"
                ]
            },
            {
                "core_activity": "Assessment of research",
                "color":"#FFD1DC",
                "activities":[ 
                    "Assessing doctoral theses (national or international)",
                    "Reviewing journal and conference papers",
                    "Organizing national and international travelling"
                    
                ]
            },
            {
                "core_activity": "Execution of research",
                "color":"#FAEBD7",
                "activities":[ 
                    "Conducting research",
                    "Driving and managing academic and research support staff",
                    "Ensuring the application of the quality system in respect of the research",
                    "Monitoring the academic integrity of the research in respect of external stakeholders",
                    "Drafting publications and giving lectures at national and international conferences",
                    "Consulting with the chair of the capacity group regarding progress of research within the chair and taking action to calibrate efforts on that basis",
                    "coordinating with the Director of the research institute regarding the staffing to be provided for the execution of the research",
                    "Coordinating the research question and working hypotheses with the (associate) Professor",
                    "Creating a literature review, attending symposiums and conferences and discussions with experts",
                    "Formulating the research question, working hypotheses and specifying the research data required, research methods and target groups",
                    "Exchanging knowledge with fellow national and international researchers and experts",
                    "Safeguarding the academic integrity of the research"
                ]
            },
            {
                "core_activity": "Publication of research",
                "color":"#c1e6c2",
                "activities":[ 
                    "Drafting publications for recognised academic journals and trade journals",
                    "Drafting conference papers and giving lectures at conferences",
                    "Drafting other publications",
                    "Checking status of publications",
                    "Giving presentations at external organisations",
                    "Adapting the publication following responses from reviewers and fellow researchers",
                    "Making agreements with external parties, if present, regarding the publication of research results",
                    "Organizing national and international travelling"
                ]
            },
            {
                "core_activity": "Research coordination",
                "color":"#F0E68C",
                "activities":[ 
                    "Structuring the research in research subquestions",
                    "Encouraging coordination between substudies",
                    "Improving the cohesion, both in terms of methodology and content, between substudies",
                    "Assigning job assignments and giving instructions as well as monitoring the progress and quality of their execution by academic and research support staff",
                    "Participating in the recruitment, selection and assessment of research support staff",
                    "Coordinating with other research or substudies",
                    "Assigning responsibilities and giving instructions to academic and research support staff",
                    "Monitoring the progress and quality of the execution of job assignments issued to academic and research support staff"
                ]
            },
            {
                "core_activity": "Research proposal",
                "color":"#F5DEB3",
                "activities":[ 
                    "Becoming informed on subject matter by a literature review, attending symposiums, conducting interviews with experts",
                    "Following specific courses",
                    "Formulating a research question",
                    "Co-authoring research proposals for further research"

                ]
            },
            {
                "core_activity": "Research plan",
                "color":"#FFF5EE",
                "activities":[ 
                    "Becoming familiar with existing methodologies",
                    "Formulating working hypotheses and specifying the necessary research data",
                    "Exchanging knowledge with fellow researchers and subject matter experts",
                    "Making agreements with target groups and stakeholders",
                    "Drafting and coordinating the schedule and action plan with the supervisor/committee of the research institute/the research school",
                ]
            },
            {
                "core_activity": "Performing research",
                "color":"#FFE4E1",
                "activities":[ 
                    "Contributing knowledge to research by others within the capacity group",
                    "Assessing the quality of the research data collected",
                    "Documenting the data in a research journal",
                    "Updating and calibrating research methodologies and research instruments",
                    "Periodically discussing research results with fellow researchers and supervisor or co-supervisor"
                ]
            },
            {
                "core_activity": "Doctoral thesis",
                "color":"#FAFAD2",
                "activities":[ 
                    "Writing draft chapters",
                    "Discussing any draft chapters with the supervisor or co-supervisors",
                    "Amending drafts",
                    "Responding to the questions of the Doctoral Committee"
                ]
            }

        ]
    }

    add_unspecify(dicc_core)
    dicc_subact, dicc_map_subact = create_dicc_subactivities(dicc_core)
    dicc_core_color = create_dicc_color(dicc_core)

    return dicc_core, dicc_subact, dicc_map_subact, dicc_core_color