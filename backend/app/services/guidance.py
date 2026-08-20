from typing import List, Dict, Any
from app.schemas.enums import IncidentCategory, SeverityLevel
from app.schemas.emergency import EmergencyGuidance, GuidanceStep

GUIDANCE_DATABASE: Dict[IncidentCategory, Dict[str, Any]] = {
    IncidentCategory.PUNCTURE: {
        "summary": "Park safely on the road shoulder, turn on hazard lights, and secure the vehicle before attempting tire replacement or contacting roadside puncture repair.",
        "do_not": [
            "Do NOT stop abruptly in the middle of active traffic lanes.",
            "Do NOT attempt to change the tire if parked on an incline without wheel chocks."
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Safety Positioning",
                "instruction": "Pull over safely to the far left shoulder. Turn on hazard warning lights immediately.",
                "caution": "Stay inside the vehicle if on a high-speed express highway until safe.",
                "is_critical": True
            },
            {
                "step_number": 2,
                "title": "Secure Vehicle",
                "instruction": "Engage the handbrake firmly and place the vehicle in 1st gear (or Park for automatics).",
                "caution": None,
                "is_critical": False
            },
            {
                "step_number": 3,
                "title": "Request Assistance",
                "instruction": "Contact nearby mobile puncture repair vendor or deploy spare wheel if equipped with jack and lug wrench.",
                "caution": None,
                "is_critical": False
            }
        ]
    },
    IncidentCategory.ACCIDENT: {
        "summary": "Assess casualties immediately, secure the crash zone, call 112 emergency services, and provide first-aid while awaiting ambulance arrival.",
        "do_not": [
            "Do NOT move severely injured victims unless there is immediate fire/explosion danger.",
            "Do NOT remove helmets of unconscious motorbystanders."
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Call Emergency Services (112)",
                "instruction": "Immediately dial 112 for Police and Ambulance. Provide exact GPS location coordinates.",
                "caution": "Keep phone line open for dispatch instructions.",
                "is_critical": True
            },
            {
                "step_number": 2,
                "title": "Check Airway & Bleeding",
                "instruction": "Apply direct firm pressure with clean cloth over bleeding wounds.",
                "caution": "Do not apply tight tourniquets unless trained.",
                "is_critical": True
            },
            {
                "step_number": 3,
                "title": "Warn Oncoming Traffic",
                "instruction": "Place reflective hazard triangles 50 meters behind the crash scene.",
                "caution": "Watch out for passing vehicles.",
                "is_critical": False
            }
        ]
    },
    IncidentCategory.BREAKDOWN: {
        "summary": "Turn on hazard lights, move vehicle to safe area, raise bonnet to signal breakdown, and request towing/mechanic service.",
        "do_not": [
            "Do NOT open hot radiator caps when engine overheats.",
            "Do NOT leave vehicle unattended in unlit isolated areas."
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Signal Emergency",
                "instruction": "Turn on hazard lights and open vehicle bonnet to signal breakdown to passing help.",
                "caution": None,
                "is_critical": False
            },
            {
                "step_number": 2,
                "title": "Contact RSA / Towing",
                "instruction": "Dispatch nearest mechanic or flatbed towing truck via RAAHAT provider list.",
                "caution": None,
                "is_critical": False
            }
        ]
    }
}

class GuidanceEngine:
    def get_guidance(self, category: IncidentCategory, severity: SeverityLevel) -> EmergencyGuidance:
        data = GUIDANCE_DATABASE.get(category, GUIDANCE_DATABASE[IncidentCategory.BREAKDOWN])
        
        steps = [
            GuidanceStep(
                step_number=item["step_number"],
                title=item["title"],
                instruction=item["instruction"],
                caution=item.get("caution"),
                is_critical=item.get("is_critical", False)
            )
            for item in data["steps"]
        ]
        
        return EmergencyGuidance(
            summary=data["summary"],
            immediate_do_not_do=data["do_not"],
            steps=steps,
            first_aid_included=(category in [IncidentCategory.ACCIDENT, IncidentCategory.MEDICAL])
        )

guidance_engine = GuidanceEngine()
