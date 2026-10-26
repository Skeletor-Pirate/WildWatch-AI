class FallbackLogic:
    """
    Offline Edge Fallback Controller:
    Ensures that when internet or uplink drops, the edge node still protects
    villagers by autonomously flashing strobes and sounding buzzers for verified dangerous megafauna.
    """
    def __init__(self, actuators):
        self.actuators = actuators

    def handle_offline_event(self, event):
        cls = event.get('class') or event.get('edge_class', '')
        conf = float(event.get('conf') or event.get('edge_conf', 0))
        
        # High hazard wildlife encounters in forest-edge corridors
        if cls in ['elephant', 'leopard', 'tiger', 'bear', 'sloth_bear'] and conf > 0.55:
            print(f"[Offline Fallback] Critical threat ({cls.upper()}) detected offline! Triggering autonomous Strobe & Siren.")
            self.actuators.trigger('strobe_pin')
            self.actuators.trigger('buzzer_pin')
        elif cls in ['wild_boar', 'nilgai', 'deer'] and conf > 0.5:
            print(f"[Offline Fallback] Herbivore ({cls}) approaching crop boundary. Triggering mild acoustic pulse.")
            self.actuators.trigger('buzzer_pin')