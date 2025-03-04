tools = [
    {
        "type": "function",
        "function": {
            "name": "get_dataset_info",
            "description": "Retrieve available case studies, themes, topics, and platforms.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compute_overall_statistics",
            "description": "Compute statistics on total guidelines and distribution by platform.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rank_case_studies_by_impact",
            "description": "Ranks case studies by impact/performance, supporting sorting and grouping options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Group by platform, theme, or topic (e.g., ['Citation Code: Platform-Specific', 'Catalog Theme Title'])."
                    },
                    "ascending": {
                        "type": "boolean",
                        "description": "Sort impact in ascending order (low to high) or descending order (high to low). Default is descending."
                    }
                },
                "required": []
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "compare_guideline_across_sites",
            "description": "Compare how different sites implement a specific guideline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "guideline_id": {"type": "string", "description": "The ID or title of the guideline to compare."},
                    "platform": {
                        "type": "string",
                        "enum": ["desktop", "mobile", "app"],
                        "description": "The platform to filter by (optional)."
                    }
                },
                "required": ["guideline_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_guideline",
            "description": "Search guidelines by title, theme, or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "The term to search in guideline titles, themes, or topics."}
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_theme_guidelines",
            "description": "Retrieve guidelines within a specific theme or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "description": "The theme to filter guidelines by."},
                    "topic": {"type": "string", "description": "The topic within the theme to filter by (optional)."}
                },
                "required": ["theme"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_guidelines_by_criteria",
            "description": "Filter guidelines based on impact, cost, adherence, and other criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "description": "The theme to filter by (optional)."},
                    "topic": {"type": "string", "description": "The topic to filter by (optional)."},
                    "platform": {
                        "type": "string",
                        "enum": ["desktop", "mobile", "app"],
                        "description": "The platform to filter by (optional)."
                    },
                    "low_cost": {"type": "boolean", "description": "Filter for low-cost guidelines (optional)."},
                    "high_impact": {"type": "boolean", "description": "Filter for high-impact guidelines (optional)."},
                    "violated": {"type": "boolean", "description": "Filter for violated guidelines (optional)."},
                    "adhered": {"type": "boolean", "description": "Filter for adhered guidelines (optional)."},
                    "na": {"type": "boolean", "description": "Filter for guidelines marked as N/A (optional)."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_site_adherence",
            "description": "Analyze how different sites adhere to or violate guidelines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["adhered", "violated"],
                        "description": "The adherence status to filter by."
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["desktop", "mobile", "app"],
                        "description": "The platform to filter by (optional)."
                    },
                    "low_cost": {"type": "boolean", "description": "Filter for low-cost guidelines (optional)."},
                    "high_impact": {"type": "boolean", "description": "Filter for high-impact guidelines (optional)."}
                },
                "required": ["status"]
            }
        }
    }
]
