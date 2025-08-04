import random
from cards import CardInPlay


class Zone:
    def __init__(self, name, max_size=None, is_visible=True, allowed_types=None, maintains_order=True):
        self.name = name
        self.cards = []
        self.max_size = max_size
        self.is_visible = is_visible
        self.allowed_types = allowed_types or []  # Lista de tipos permitidos
        self.maintains_order = maintains_order
        
    def can_add(self):
        if self.max_size:
            return len(self.cards) < int(self.max_size)    
        else:
            return True
        
        
    def add_cards(self, card_list):
        self.cards = card_list + self.cards
        
    
    def add_cards_to_bottom(self, card_list):
        self.cards = self.cards + card_list
        return
        
        
    def remove_by_id(self, id):
        for card in self.cards:
            if card.instance_id == id:
                recover_card = card
                self.cards.remove(card)
                return [recover_card]
            
        # crear un error personalizado
        print(f"Error: carta {id} no encontrada")
        return False
    
            
    def remove_all(self):
        recover_cards = self.cards
        self.cards = []
        return recover_cards
    
    
    def remove_amount(self, count=1):
        if count > len(self.cards):
            # crear un error personalizado
            print("Not enough cards in the deck to draw.")
            return False
        
        drawn_cards = self.cards[:count]
        self.cards = self.cards[count:]
        
        return drawn_cards
    
    
    def get_card_info_by_id(self, card_id):
        for card in self.cards:
            if card.instance_id == card_id:
                return card
            
        print("Carta no encontrada")
        return False
    

    def shuffle(self):
        random.shuffle(self.cards)
        
        
    def see_cards(self):
        return self.cards
        
        
    def __len__(self):
        return len(self.cards)
    
    
    def __str__(self) -> str:
        return self.name
      
        

class Deck(Zone):
    """ 
    Conjunto de cartas que el jugador utiliza para juga: 
    """
    def __init__(self, cards):
        super().__init__(
            name = "Mazo",
            max_size = 45,
            is_visible = False,
            allowed_types = ["UNIDAD", "MONUMENTO", "ACCION"],
            maintains_order = True
        )
        
        self.cards = cards
        

class TokenDeck(Zone):
    """ 
    Conjunto de tokens
    """
    def __init__(self, cards):
        super().__init__(
            name = "Tokens",
            max_size = None,
            is_visible = False,
            allowed_types = ["TOKEN"],
            maintains_order = False
        )
        
        self.cards = cards
        

class TreasuresDeck(Zone):
    """ 
    Conjunto de cartas de tesoro 
    """
    def __init__(self, cards):
        super().__init__(
            name = "Boveda",
            max_size = 15,
            is_visible = False,
            allowed_types = ["TESORO"],
            maintains_order = True
        )
        
        self.cards = cards
        
        
class DiscardManager(Zone):
    """ 
    Almacena cartas descartadas/destruidas: 
    """
    def __init__(self) -> None:
        super().__init__(
            name = "Descarte",
            max_size = None,
            is_visible = True,
            allowed_types = ["UNIDAD", "MONUMENTO", "ACCION"],
            maintains_order = True
        )
        

class ReserveTreasuresManager(Zone):
    """ 
    Almacena cartas de tesoro: 
    """
    def __init__(self) -> None:
        super().__init__(
            name = "Reserva",
            max_size = 7,
            is_visible = True,
            allowed_types = ["TESORO"],
            maintains_order = False
        )
    

class OutTreasuresManager(Zone):
    """ 
    Almacena cartas de tesoros agotados: 
    """
    def __init__(self) -> None:
        super().__init__(
            name = "Tesoros Agotados",
            max_size = None,
            is_visible = False,
            allowed_types = ["TESORO"],
            maintains_order = False
        )
        

class FormationManager(Zone):
    """ 
    Almacena cartas de tesoros en juego: 
    """
    def __init__(self):
        super().__init__(
            name = "Formación",
            max_size = None,
            is_visible = True,
            allowed_types = ["UNIDAD", "MONUMENTO", "ACCION"],
            maintains_order = False
        )
        
        
    # TODO: terminar funcion ver efectos al jugar una carta
    def add_card_to_play(self, card):
        """Convierte una carta en CardInPlay y la añade"""
        if self.can_add():
            card_in_play = CardInPlay(card)
            self.cards.append(card_in_play)
            
            # Ejecutar efecto de aparición si lo tiene
            if card.has_enter_play_effect():
                card.on_enter_play()
                
            if card.type == "UNIDAD":
                card_in_play.can_attack = card.has_frenzy()
            
            return card_in_play
        return None
    
    def get_units_that_can_attack(self):
        """Retorna unidades que pueden atacar"""
        return [card_in_play for card_in_play in self.cards 
                if card_in_play.can_attack_now()]
    
    def reset_all_for_new_turn(self):
        """Resetea todas las cartas para nuevo turno"""
        for card_in_play in self.cards:
            card_in_play.reset_for_new_turn()


class CombatManager(Zone):
    """
    Almacena cartas en juego y en combate
    """
    def __init__(self):
        super().__init__(
            name = "Combate",
            max_size = None,
            is_visible = True,
            allowed_types = ["UNIDAD", "MONUMENTO", "ACCION"],
            maintains_order = False
        )
        
        self.attackers = []
        self.defenders = {}
        

class HandManager(Zone):
    def __init__(self):
        super().__init__(
            name = "Mazo",
            max_size = 7,
            is_visible = True,
            allowed_types = ["UNIDAD", "MONUMENTO", "ACCION"],
            maintains_order = False
        )
        self.mulligan_used = False
        self.cards = []
        self.realeza = False
        
    def add_cards(self, card_list):
        if len(self.cards) < self.max_size:
            space = self.max_size - len(self.cards)
            to_add = card_list[:space]
            self.cards.extend(to_add)
            
            # Las que no entraron
            leftovers = card_list[space:]
            return leftovers
        else:
            # crear un error personalizado
            print("Cannot add card: hand is full.")
            return False
    

class HealthManager:
    def __init__(self, initial_life=20):
        self.life_points = initial_life
        
    def remove_life_points(self, points):    
        self.life_points -= points
        
    def add_life_points(self, points):    
        self.life_points += points
        
    def life_status(self):
        return self.life_points > 0
    
    def __str__(self):
        return f"{self.life_points})"



class PlayerResources:
    """ Maneja oro, vida """
    def __init__(self) -> None:
        self.health = HealthManager()
        self.available_gold = 0
        
    def spend_gold(self, count):
        if self.available_gold >= count:
            self.available_gold -= count
            return True
        return False

    def add_gold(self, count=1):
        self.available_gold += count
        return True
        
        
class PlayerZones:
    """ maneja las zonas del jugador """
    def __init__(self, cards, treasures, token_cards) -> None:
        # Mazo de reino y bóveda de tesoros
        self.mazo = Deck(cards)
        self.boveda = TreasuresDeck(treasures)
        self.tokens = TokenDeck(token_cards)
        
        # Mano del jugador
        self.hand = HandManager()
        
        # Zonas principales
        self.formacion = FormationManager()
        self.combate = CombatManager()
        self.reserva_tesoros = ReserveTreasuresManager()
        self.tesoros_agotados = OutTreasuresManager()
        self.descarte = DiscardManager()

    def move_card(self, from_zone, to_zone, card_id=None, amount=1):
        if to_zone.can_add():
            if card_id:
                card = from_zone.remove_by_id(card_id)
            else:
                card = from_zone.remove_amount(amount)
            
            if card:
                if from_zone == self.hand and to_zone == self.formacion:
                    # Añadir carta a la formación
                    card_in_play = to_zone.add_card_to_play(card[0])
                    if card_in_play:
                        return True
                leftovers = to_zone.add_cards(card)
                if isinstance(leftovers, list):
                    # agregar lestovers al mazo to zone
                    from_zone.add_cards(leftovers)
                    
                return True
        
        print(f"{to_zone} completa")
        return False
            
            
    def move_card_to_bottom(self, from_zone, to_zone, card_id):
        if to_zone.can_add():
            card = from_zone.remove_by_id(card_id)
            to_zone.add_cards_to_bottom([card])
            return True
        return False
            
            
    def move_all_cards(self, from_zone, to_zone):
        if to_zone.can_add():
            cards = from_zone.remove_all()
            to_zone.add_cards(cards)
            return True
        return False
            
            
    def retornar_tesoros_agotados(self):
        return self.move_all_cards(self.tesoros_agotados, self.reserva_tesoros)
        
    
    def retornar_unidades_a_formacion(self):
        return self.move_all_cards(self.combate, self.formacion)
    
    
    def _activar_ataque(self):
        for card in self.formacion.cards:
            card.reset_for_new_turn()
            
    
    def clean_turn(self):
        self.retornar_tesoros_agotados()
        self.retornar_unidades_a_formacion()
        self._activar_ataque()



class PlayerActions:
    def __init__(self, zones, resources) -> None:
        self.zones = zones
        self.resources = resources
        
        
    def draw_card_from_mazo(self, count=1):
        draw_action = self.zones.move_card(
            from_zone=self.zones.mazo,
            to_zone=self.zones.hand,
            amount=count
        )
        return draw_action
        
        
    def play_card_from_hand(self, card_id):
        card = self.zones.hand.get_card_info_by_id(card_id)
        if self.zones.hand.realeza and card.supertype == "REALEZA":
            print("SOLO UNA CARTA DE REALEZA")
            return False
        if card and card.can_be_played(self.resources.available_gold):
            # Coordina: mover carta + gastar oro
            play_action = self.zones.move_card(self.zones.hand, self.zones.formacion, card_id)
            if card.supertype == "REALEZA":
                self.zones.hand.realeza = True
            if play_action:
                self.resources.spend_gold(card.cost)
                return True
        
        return False
    
    
    def draw_treasure(self):
        if not self.zones.reserva_tesoros.can_add():
            print("Reserva completa")
            return False
        
        card = self.zones.move_card(self.zones.boveda, self.zones.reserva_tesoros)
        return card
        
        
    def agotar_tesoro(self, card_id):
        """Mueve un tesoro de la reserva a los agotados"""
        card_selected = self.zones.reserva_tesoros.get_card_info_by_id(card_id)
        if card_selected and card_selected.type == 'TOKEN':
            result = self.zones.move_card(self.zones.reserva_tesoros, self.zones.descarte, card_id)
            if result:
                return self.resources.add_gold()
            return False
        
        card = self.zones.move_card(self.zones.reserva_tesoros, self.zones.tesoros_agotados, card_id)
        if card:
            return self.resources.add_gold()
        return False
    
    def first_turn_return_card_to_bottom(self, card_id):
        return self.zones.move_card_to_bottom(self.zones.hand, self.zones.mazo, card_id)
    
    
    def mulligan(self):
        move_cards = self.zones.move_all_cards(self.zones.hand, self.zones.mazo)
        if move_cards:
            self.zones.mazo.shuffle()
            self.zones.hand.mulligan_used = True
            return True
        return move_cards
    
    
    def attack_with_unit(self, card_id):
        card = self.zones.formacion.get_card_info_by_id(card_id)
        if card and card.can_attack_now():
            # Coordina: mover carta + gastar oro
            card_selected = self.zones.move_card(self.zones.formacion, self.zones.combate, card_id)
            if card_selected:
                return True
        return False
    
    
    def get_token(self):
        return self.zones.move_card(self.zones.tokens, self.zones.reserva_tesoros)
    
    # def use_token(self, card_id):
    #     token = self.zones.reserva_tesoros.get_card_info_by_id(card_id)
    #     if token and token.type == 'TOKEN':
    #         return self.zones.move_card(self.zones.reserva_tesoros, self.zones.descarte, card_id)
    #     return False
    




class Player:
    def __init__(self, name, cards, treasures, tokens):
        self.name = name
        self.resources = PlayerResources()
        self.zones = PlayerZones(cards, treasures, tokens)
        self.actions = PlayerActions(self.zones, self.resources)
        
        
    def get_player_input(self, message):
        return input(f'{message}: ')
    
    def get_player_gold(self):
        return self.resources.available_gold
    
    def __str__(self):
        return f"Player(name={self.name}, life={self.resources.health})"
        
