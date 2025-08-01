from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd

from utils import generate_instance_id


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
    
    @abstractmethod
    def can_be_played(self, available_gold: int) -> bool:
        """Verifica si la carta puede ser jugada con el oro disponible"""
        pass
    
    def has_enter_play_effect(self) -> bool:
        """Verifica si la carta tiene efecto de 'Aparición en juego'"""
        return "Aparición en juego:" in self.text
    
    def on_enter_play(self):
        """Ejecuta el efecto de aparición en juego (a implementar en subclases si es necesario)"""
        pass
    
    def __str__(self) -> str:
        return f"{self.name} | type: {self.type}"


@dataclass
class Unit(Card):
    """Cartas de tipo UNIDAD - criaturas que van al Reino"""
    strength: int
    toughness: int
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost
    
    def can_attack(self) -> bool:
        """Verifica si la unidad puede atacar"""
        return True  # Por defecto, todas las unidades pueden atacar
    
    def has_frenzy(self) -> bool:
        """Verifica si tiene la habilidad Frenesí"""
        return "Frenesí" in self.text
    
    def has_stealth(self) -> bool:
        """Verifica si tiene la habilidad Sorpresivo"""
        return "Sorpresivo" in self.text
    
    def has_theft(self) -> bool:
        """Verifica si tiene la habilidad Hurto"""
        return "Hurto" in self.text
    
    def has_evasion(self) -> bool:
        """Verifica si tiene la habilidad Evasión"""
        return "Evasión" in self.text


@dataclass
class Monument(Card):
    """Cartas de tipo MONUMENTO - estructuras permanentes"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost
    
    def has_erosion(self) -> bool:
        """Verifica si tiene la habilidad Erosión"""
        return "Erosión" in self.text


@dataclass
class Action(Card):
    """Cartas de tipo ACCIÓN - efectos instantáneos"""
    
    def can_be_played(self, available_gold: int) -> bool:
        return available_gold >= self.cost
    
    def is_fast(self) -> bool:
        """Verifica si es una acción rápida"""
        return self.supertype == "RAPIDA"
    
    def resolve_effect(self):
        """Resuelve el efecto de la acción y la envía al descarte"""
        print(f"Resolviendo efecto de {self.name}")
        # Aquí iría la lógica específica del efecto


@dataclass
class Treasure(Card):
    """Cartas de tipo TESORO - van a la Zona de Reserva y generan oro"""
    
    def can_be_played(self, available_gold: int) -> bool:
        # Los tesoros se revelan automáticamente, no se "juegan"
        return True
    
    def generate_gold(self) -> int:
        """Genera oro (por defecto 1, puede ser sobrescrito)"""
        return 1
    
    def has_destroy_ability(self) -> bool:
        """Verifica si tiene habilidad de 'Destruir'"""
        return "Destruir:" in self.text


@dataclass
class Token(Card):
    """Cartas de tipo TOKEN - representan recursos o efectos temporales"""

    def can_be_played(self, available_gold: int) -> bool:
        # Los tokens se revelan automáticamente, no se "juegan"
        return True
    
    def generate_gold(self) -> int:
        """Genera oro (por defecto 1, puede ser sobrescrito)"""
        return 1
    

# No se como puedo usar esta clase
class CardInPlay:
    _next_id = 1  # Variable de clase
    
    def __init__(self, card):
        self.card = card
        self.can_attack = False
        self.current_damage = 0
        self.has_attacked_this_turn = False
        self.id = CardInPlay._next_id
        CardInPlay._next_id += 1
    
    # Métodos de conveniencia para acceder a propiedades de la carta
    @property
    def name(self):
        return self.card.name
    
    @property
    def cost(self):
        return self.card.cost
    
    @property
    def type(self):
        return self.card.type
    
    @property
    def instance_id(self):
        return self.card.instance_id
    
    @property
    def get_strength_toughness(self):
        if isinstance(self.card, Unit):
            return (self.card.strength, self.card.toughness)
        return (0, 0)


    def take_damage(self, amount):
        """Aplica daño a la carta"""
        if isinstance(self.card, Unit):
            self.current_damage += amount
            return self.current_damage >= self.card.strength
        
    def can_attack_now(self):
        """Verifica si puede atacar en este momento"""
        return (self.can_attack and 
                not self.has_attacked_this_turn and
                isinstance(self.card, Unit))
        
    def reset_for_new_turn(self):
        """Resetea estado para nuevo turno"""
        self.can_attack = True
        self.has_attacked_this_turn = False
        self.current_damage = 0
        
    def __str__(self):
        if isinstance(self.card, Unit):
            damage_str = f" ({self.current_damage} daño)" if self.current_damage > 0 else ""
            return f"{self.card.name} [{self.card.strength}/{self.card.toughness}]{damage_str}"
        return f"{self.card.name}"


def load_cards(path_csv: str):
    df = pd.read_csv(path_csv)
    cards: list[Card] = []
    tresure_cards: list[Card] = []
    token_cards: list[Card] = []
    
    for _, row in df.iterrows():
        card_type = row['Tipo']
        
        # Datos comunes para todas las cartas
        common_data = {
            'name': row['Nombre'],
            'cost': int(row['Coste']),
            'text': row['Texto'],
            'expansion': row['Expansión'],
            'rareness': row['Rareza'],
            'type': row['Tipo'],
            'supertype': row.get('Supertipo') if pd.notna(row.get('Supertipo')) else None,
            'subtype_1': row.get('Subtipo 1') if pd.notna(row.get('Subtipo 1')) else None,
            'subtype_2': row.get('Subtipo 2') if pd.notna(row.get('Subtipo 2')) else None,
            'clarification': row.get('Aclaraciones') if pd.notna(row.get('Aclaraciones')) else None,
            'instance_id': next(generate_instance_id),
        }
        
        # Crear la instancia específica según el tipo
        if card_type == 'UNIDAD':
            # Manejar strength y toughness para unidades
            strength = 0
            toughness = 0
            
            if pd.notna(row['Fuerza']) and str(row['Fuerza']).strip() != '':
                strength = int(row['Fuerza'])
                
            if pd.notna(row['Resistencia']) and str(row['Resistencia']).strip() != '':
                toughness = int(row['Resistencia'])
            
            cards.append(Unit(strength=strength, toughness=toughness, **common_data))
            
        elif card_type == 'MONUMENTO':
            cards.append(Monument(**common_data))
            
        elif card_type == 'ACCION':
            cards.append(Action(**common_data))
            
        elif card_type == 'TESORO':
            tresure_cards.append(Treasure(**common_data))
            
        elif card_type == 'TOKEN':
            token_cards.append(Token(**common_data))
        
        else:
            print(f"Tipo de carta desconocido: {card_type}")

    return (cards, tresure_cards, token_cards)
