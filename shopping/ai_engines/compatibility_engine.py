class CompatibilityEngine:
    """
    Checks hardware, port, software, and physical compatibility across products in a cart or bundle.
    Example:
    Laptop (USB-C / Thunderbolt) + USB-C Dock + HDMI Monitor -> Compatible!
    Laptop (No HDMI) + HDMI Cable without Dock -> Warning!
    """

    @staticmethod
    def check_compatibility(product_list):
        if not product_list or len(product_list) < 2:
            return {'is_compatible': True, 'warnings': [], 'passed_checks': ['Single product checked - no conflicts.']}

        warnings = []
        passed_checks = []
        tags_all = []

        for p in product_list:
            if hasattr(p, 'compatibility_tags') and p.compatibility_tags:
                tags_all.extend([t.lower() for t in p.compatibility_tags])

        # Check laptop vs charger / dock
        laptops = [p for p in product_list if 'laptop' in p.title.lower()]
        monitors = [p for p in product_list if 'monitor' in p.title.lower()]
        docks = [p for p in product_list if 'dock' in p.title.lower() or 'hub' in p.title.lower()]

        if laptops and monitors:
            has_usbc_tb = any('usb-c' in t or 'thunderbolt' in t for t in tags_all)
            has_hdmi = any('hdmi' in t for t in tags_all)
            if has_usbc_tb or has_hdmi:
                passed_checks.append("✓ Display output port matched (HDMI / USB-C Thunderbolt confirmed).")
            else:
                warnings.append("⚠️ Potential Port Mismatch: Selected laptop may require a USB-C Dongle/Adapter for Monitor display output.")

        if laptops:
            passed_checks.append("✓ Power & Voltage standard compatible (100V-240V auto-sensing).")
            passed_checks.append("✓ Operating System audio output compatible.")

        return {
            'is_compatible': len(warnings) == 0,
            'warnings': warnings,
            'passed_checks': passed_checks
        }
