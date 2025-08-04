from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import re
import pandas as pd
from utils import generate_instance_id


class EffectType(Enum):
    STATIC = "static"
    TRIGGERED = "triggered"
    ACTIVATED = "activated"
    GOLD_GENERATING = "gold_generating"

class TriggerCondition(Enum):
    ENTER_PLAY = "enter_play"
    DESTROYED = "destroyed"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    COMBAT_START = "combat_start"
    ATTACK_DECLARED = "attack_declared"
    DAMAGE_DEALT = "damage_dealt"
    CARD_DRAWN = "card_drawn"
    
    
@dataclass
class Effect:
    """Representa un efecto individual de una carta"""
    effect_type: EffectType
    trigger_condition: Optional[TriggerCondition] = None
    cost: Optional[str] = None  # Para habilidades activadas
    condition: Optional[str] = None  # Condiciones adicionales
    effect_text: str = ""
    targets_required: int = 0
    is_optional: bool = False
    
class EffectParser:
    """Parser para extraer efectos del texto de las cartas"""
    
    # Patrones para detectar diferentes tipos de efectos
    TRIGGERED_PATTERNS = {
        TriggerCondition.ENTER_PLAY: r"Aparición en juego:\s*(.+?)(?:\.|$)",
        TriggerCondition.DESTROYED: r"Derrotado:\s*(.+?)(?:\.|$)",
        TriggerCondition.TURN_START: r"Al inicio de tu (?:primera )?fase central,?\s*(.+?)(?:\.|$)",
        TriggerCondition.DAMAGE_DEALT: r"Siempre que (?:esta carta|[^,]+) (?:haga|cause) daño,?\s*(.+?)(?:\.|$)",
    }
    
    ACTIVATED_PATTERNS = [
        r"(.+?):\s*(.+?)(?:\.|$)",  # Patrón general: "Coste: Efecto"
        r"Destruir:\s*(.+?)(?:\.|$)",  # Patrón específico para destruir
        r"Agotar:\s*(.+?)(?:\.|$)",   # Patrón para agotar
    ]
    
    STATIC_KEYWORDS = [
        "Temible", "Frenesí", "Evasión", "Arrollar", "Centinela", 
        "Curar", "Guardián", "Indestructible", "Sorpresivo"
    ]
    
    GOLD_GENERATION_PATTERNS = [
        r"Genera\s+(\d+)\s*(?:de oro|oro)?",
        r"Destruir:\s*Genera\s+(\d+)",
    ]
    
    @classmethod
    def parse_effects(cls, text: str) -> List[Effect]:
        """Extrae todos los efectos del texto de una carta"""
        effects = []
        
        # 1. Buscar efectos disparados
        for condition, pattern in cls.TRIGGERED_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                effect_text = match.group(1).strip()
                targets = cls._count_targets(effect_text)
                is_optional = "puedes" in effect_text.lower()
                
                effects.append(Effect(
                    effect_type=EffectType.TRIGGERED,
                    trigger_condition=condition,
                    effect_text=effect_text,
                    targets_required=targets,
                    is_optional=is_optional
                ))
        
        # 2. Buscar efectos activados
        for pattern in cls.ACTIVATED_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    cost = match.group(1).strip()
                    effect_text = match.group(2).strip()
                else:
                    cost = "Destruir"
                    effect_text = match.group(1).strip()
                
                targets = cls._count_targets(effect_text)
                is_optional = "puedes" in effect_text.lower()
                
                # Verificar si es generadora de oro
                effect_type = EffectType.GOLD_GENERATING if any(
                    re.search(pattern, effect_text, re.IGNORECASE) 
                    for pattern in cls.GOLD_GENERATION_PATTERNS
                ) else EffectType.ACTIVATED
                
                effects.append(Effect(
                    effect_type=effect_type,
                    cost=cost,
                    effect_text=effect_text,
                    targets_required=targets,
                    is_optional=is_optional
                ))
        
        # 3. Buscar habilidades estáticas
        for keyword in cls.STATIC_KEYWORDS:
            if keyword in text:
                effects.append(Effect(
                    effect_type=EffectType.STATIC,
                    effect_text=keyword
                ))
        
        # 4. Buscar efectos estáticos con modificadores
        static_modifiers = re.finditer(
            r"(?:Las? (?:otras? )?unidades? que controlas|Todas las unidades aliadas)\s+(.+?)(?:\.|$)", 
            text, re.IGNORECASE
        )
        for match in static_modifiers:
            effects.append(Effect(
                effect_type=EffectType.STATIC,
                effect_text=match.group(0).strip()
            ))
        
        return effects
    
    @classmethod
    def _count_targets(cls, text: str) -> int:
        """Cuenta cuántos objetivos requiere un efecto"""
        target_patterns = [
            r"(?:la |el |una? |un )?(?:unidad|jugador|carta|tesoro)\s+(?:rival\s+)?objetivo",
            r"hasta (?:una?|dos|tres|cuatro|cinco|\d+) (?:unidad|carta|tesoro)(?:es)?\s+(?:rival(?:es)?\s+)?objetivo",
        ]
        
        total_targets = 0
        for pattern in target_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if "hasta" in pattern:
                # Para "hasta X", contamos como opcional (targets_required = 0)
                continue
            total_targets += len(matches)
        
        return total_targets

class EffectExecutor:
    """Ejecuta los efectos de las cartas en el contexto del juego"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.effect_handlers = self._build_effect_handlers()
    
    def _build_effect_handlers(self) -> Dict[str, Callable]:
        """Construye un diccionario de manejadores de efectos específicos"""
        return {
            # Efectos de excavación
            "excavar_boveda": self._handle_dig_vault,
            "mostrar_boveda": self._handle_show_vault,
            "intercambiar_tesoro": self._handle_swap_treasure,
            
            # Efectos de daño
            "hacer_dano": self._handle_deal_damage,
            "dano_a_unidad": self._handle_damage_unit,
            
            # Efectos de descarte
            "descartar_carta": self._handle_discard_card,
            "descartar_cartas": self._handle_discard_cards,
            
            # Efectos de retorno a mano
            "regresar_mano": self._handle_return_to_hand,
            
            # Efectos de creación de fichas
            "crear_ficha": self._handle_create_token,
            
            # Efectos de búsqueda
            "buscar_carta": self._handle_search_card,
            
            # Efectos de regreso desde descarte
            "regresar_descarte": self._handle_return_from_graveyard,
            
            # Efectos de modificación de stats
            "modificar_stats": self._handle_modify_stats,
            
            # Efectos de generación de oro
            "generar_oro": self._handle_generate_gold,
        }
    
    def execute_effect(self, effect: Effect, source_card, **kwargs):
        """Ejecuta un efecto específico"""
        effect_text = effect.effect_text.lower()
        
        # Identificar qué tipo de efecto es y ejecutarlo
        if "excavar bóveda" in effect_text:
            amount = self._extract_number(effect_text, default=1)
            return self._handle_dig_vault(amount, **kwargs)
        
        elif "hace" in effect_text and "daño" in effect_text:
            damage = self._extract_number(effect_text, default=1)
            return self._handle_deal_damage(damage, **kwargs)
        
        elif "regresa" in effect_text and "mano" in effect_text:
            return self._handle_return_to_hand(**kwargs)
        
        elif "descarta" in effect_text:
            amount = self._extract_number(effect_text, default=1)
            return self._handle_discard_cards(amount, **kwargs)
        
        elif "crea" in effect_text and "ficha" in effect_text:
            token_type = self._extract_token_type(effect_text)
            amount = self._extract_number(effect_text, default=1)
            return self._handle_create_token(token_type, amount, **kwargs)
        
        elif "genera" in effect_text and "oro" in effect_text:
            amount = self._extract_number(effect_text, default=1)
            return self._handle_generate_gold(amount, **kwargs)
        
        else:
            print(f"Efecto no implementado: {effect.effect_text}")
            return False
    
    def _extract_number(self, text: str, default: int = 1) -> int:
        """Extrae un número del texto"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else default
    
    def _extract_token_type(self, text: str) -> str:
        """Extrae el tipo de ficha del texto"""
        if "libro" in text:
            return "libro"
        elif "oro" in text:
            return "oro"
        return "genérica"
    
    # Manejadores específicos de efectos (simplificados para el ejemplo)
    def _handle_dig_vault(self, amount: int, **kwargs):
        print(f"Excavando bóveda {amount}")
        return True
    
    def _handle_show_vault(self, **kwargs):
        print("Mostrando primera carta de bóveda")
        return True
    
    def _handle_swap_treasure(self, **kwargs):
        print("Intercambiando tesoro")
        return True
    
    def _handle_deal_damage(self, damage: int, target=None, **kwargs):
        print(f"Haciendo {damage} daño a {target}")
        return True
    
    def _handle_damage_unit(self, damage: int, target=None, **kwargs):
        print(f"Haciendo {damage} daño a unidad {target}")
        return True
    
    def _handle_discard_card(self, target_player=None, **kwargs):
        print(f"Jugador {target_player} descarta una carta")
        return True
    
    def _handle_discard_cards(self, amount: int, target_player=None, **kwargs):
        print(f"Jugador {target_player} descarta {amount} cartas")
        return True
    
    def _handle_return_to_hand(self, target=None, **kwargs):
        print(f"Regresando {target} a la mano")
        return True
    
    def _handle_create_token(self, token_type: str, amount: int, **kwargs):
        print(f"Creando {amount} ficha(s) de {token_type}")
        return True
    
    def _handle_search_card(self, card_type: str, **kwargs):
        print(f"Buscando carta de tipo {card_type}")
        return True
    
    def _handle_return_from_graveyard(self, card_type: str = None, **kwargs):
        print(f"Regresando carta de {card_type} del descarte")
        return True
    
    def _handle_modify_stats(self, strength_mod: int, toughness_mod: int, target=None, **kwargs):
        print(f"Modificando stats de {target}: {strength_mod:+d}/{toughness_mod:+d}")
        return True
    
    def _handle_generate_gold(self, amount: int, **kwargs):
        print(f"Generando {amount} oro")
        return True

# Actualización de las clases de cartas
@dataclass
class Card(ABC):
    """Clase base abstracta para todas las cartas"""
    name: str
    cost: int
    text: str
    expansion: str
    rareness: str
    type: str
    supertype: Optional[str]
    subtype_1: Optional[str]
    subtype_2: Optional[str]
    clarification: Optional[str]
    instance_id: str
    effects: List[Effect] = field(default_factory=list)
    
    def __post_init__(self):
        """Parsea los efectos después de la inicialización"""
        self.effects = EffectParser.parse_effects(self.text)
    
    @abstractmethod
    def can_be_played(self, available_gold: int) -> bool:
        """Verifica si la carta puede ser jugada con el oro disponible"""
        pass
    
    def get_effects_by_type(self, effect_type: EffectType) -> List[Effect]:
        """Obtiene todos los efectos de un tipo específico"""
        return [effect for effect in self.effects if effect.effect_type == effect_type]
    
    def get_triggered_effects(self, trigger: TriggerCondition) -> List[Effect]:
        """Obtiene efectos disparados por una condición específica"""
        return [effect for effect in self.effects 
                if effect.effect_type == EffectType.TRIGGERED and 
                effect.trigger_condition == trigger]
    
    def has_static_ability(self, ability_name: str) -> bool:
        """Verifica si tiene una habilidad estática específica"""
        return any(effect.effect_text == ability_name 
                  for effect in self.effects 
                  if effect.effect_type == EffectType.STATIC)
    
    def execute_triggered_effects(self, trigger: TriggerCondition, executor: EffectExecutor, **kwargs):
        """Ejecuta todos los efectos disparados por una condición"""
        triggered_effects = self.get_triggered_effects(trigger)
        for effect in triggered_effects:
            executor.execute_effect(effect, self, **kwargs)
    
    def can_activate_ability(self, cost_description: str) -> bool:
        """Verifica si se puede activar una habilidad con el coste dado"""
        activated_effects = self.get_effects_by_type(EffectType.ACTIVATED)
        return any(effect.cost == cost_description for effect in activated_effects)
    
    def __str__(self) -> str:
        effects_str = f" [{len(self.effects)} efectos]" if self.effects else ""
        return f"{self.name} | type: {self.type}{effects_str}"

# El resto de las clases se mantienen igual pero heredan la nueva funcionalidad
@dataclass
class Unit(Card):
    """Cartas de tipo UNIDAD - criaturas que van al Reino"""
    strength: int
    toughness: int
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost

@dataclass
class Monument(Card):
    """Cartas de tipo MONUMENTO - estructuras permanentes"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost

@dataclass
class Action(Card):
    """Cartas de tipo ACCIÓN - efectos instantáneos"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost
    
    def is_fast(self) -> bool:
        """Verifica si es una acción rápida"""
        return self.supertype == "RAPIDA"

@dataclass
class Treasure(Card):
    """Cartas de tipo TESORO - van a la Zona de Reserva y generan oro"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return True
    
    def get_gold_generation_amount(self) -> int:
        """Obtiene la cantidad de oro que genera este tesoro"""
        gold_effects = self.get_effects_by_type(EffectType.GOLD_GENERATING)
        if gold_effects:
            # Extrae el número del efecto de generación de oro
            for effect in gold_effects:
                numbers = re.findall(r'\d+', effect.effect_text)
                if numbers:
                    return int(numbers[0])
        return 1  # Por defecto genera 1

@dataclass
class Token(Card):
    """Cartas de tipo TOKEN - representan recursos o efectos temporales"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return True

# Ejemplo de uso
def test_effect_parsing():
    """Función de prueba para el sistema de efectos"""
    
    # Carta de ejemplo con múltiples efectos
    test_card = Unit(
        name="Mago de Prueba",
        cost=3,
        text="Aparición en juego: Hace 2 daños a la unidad rival objetivo. Temible. Destruir: Regresa una carta de tu descarte a tu mano.",
        expansion="Test",
        rareness="Común",
        type="UNIDAD",
        supertype=None,
        subtype_1="Mago",
        subtype_2=None,
        clarification=None,
        instance_id="test_001",
        strength=2,
        toughness=3
    )
    
    print(f"Carta: {test_card.name}")
    print(f"Efectos encontrados: {len(test_card.effects)}")
    
    for i, effect in enumerate(test_card.effects):
        print(f"  {i+1}. Tipo: {effect.effect_type.value}")
        print(f"     Texto: {effect.effect_text}")
        if effect.trigger_condition:
            print(f"     Trigger: {effect.trigger_condition.value}")
        if effect.cost:
            print(f"     Coste: {effect.cost}")
        print()

if __name__ == "__main__":
    test_effect_parsing()