import urllib.parse

class LogoService:

    @staticmethod
    def get_company_logo(company_name, domain=None):
        """
        Generates automatic company logo URL using Clearbit Logo API or UI Avatars fallback.
        """
        clean_name = company_name.strip() if company_name else 'Company'
        
        # Check known domains
        domain_map = {
            'flipkart': 'flipkart.com',
            'amazon': 'amazon.in',
            'nykaa': 'nykaa.com',
            'myntra': 'myntra.com',
            'reliancetrends': 'reliancetrends.com',
            'ajio': 'ajio.com',
            'tata': 'tatacliq.com',
            'abc textiles': 'abctextiles.in',
            'chennai fabric': 'chennaifabrics.com',
            'premium threads': 'premiumthreads.in'
        }

        name_lower = clean_name.lower()
        matched_domain = domain
        if not matched_domain:
            for key, dom in domain_map.items():
                if key in name_lower:
                    matched_domain = dom
                    break

        if matched_domain:
            return f"https://logo.clearbit.com/{matched_domain}"
        
        # High quality initials avatar badge
        encoded = urllib.parse.quote(clean_name)
        return f"https://ui-avatars.com/api/?name={encoded}&background=0f172a&color=38bdf8&size=128&bold=true&font-size=0.45"
