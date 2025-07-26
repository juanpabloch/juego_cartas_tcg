from cards import load_cards
from player import Player
from phases import GameState, GamePhase, ActionType

if __name__ == "__main__":
    path = 'control_de_los_mares.csv'
    cards, treasure_cards, token_cards = load_cards(path)
    print(f"Se cargaron {len(cards)} cartas.")
    
    # Crear jugadores
    player_1 = Player("Juan pa", cards.copy(), treasure_cards, token_cards)
    player_1.zones.mazo.shuffle()
    player_1.zones.boveda.shuffle()
    
    player_2 = Player("Ema", cards.copy(), treasure_cards, token_cards)
    player_2.zones.mazo.shuffle()
    player_2.zones.boveda.shuffle()
    
    # Crear juego
    game_state = GameState(player_1, player_2)
    
    # Opciones del menú
    options = {
        "1": "Ver MANO",
        "2": "Ver RESERVA TESOROS",
        "3": "PASAR",
        "0": "Salir"
    }
    
    # Inicializar juego
    game_state._start_current_phase()
    
    # Loop principal
    while not game_state.game_over:
        print("=" * 50)
        print(f"TURNO {game_state.turn_number} | FASE: {game_state.current_phase.value.upper()}")
        print(f"JUGADOR ACTIVO: {game_state.current_player.name}")
        print("=" * 50)
        
        # Manejar acciones especiales
        if game_state.waiting_for_action == "mulligan_return":
            result = game_state._handle_mulligan_return()
            if result and not result.success:
                print(f"ERROR: {result.message}")
            continue
        
        # Menú normal
        print("\nOPCIONES:")
        for key, value in options.items():
            print(f"{key}: {value}")
        
        try:
            option_num = int(game_state.current_player.get_player_input("Selecciona opción"))
            
            if option_num == 1:
                cards_in_hand = game_state.current_player.zones.hand.see_cards()
                if cards_in_hand:
                    print("\nCARTAS EN MANO:")
                    for card in cards_in_hand:
                        print(f"- {card.name} (ID: {card.instance_id}) - Costo: {card.cost}")
                else:
                    print("No tienes cartas en la mano")
            
            elif option_num == 2:
                treasures = game_state.current_player.zones.reserva_tesoros.see_cards()
                if treasures:
                    print("\nTESOSROS EN RESERVA:")
                    for treasure in treasures:
                        print(f"- {treasure.name} (ID: {treasure.instance_id})")
                else:
                    print("No tienes tesoros en la reserva")
            
            elif option_num == 3:
                result = game_state.pass_phase()
                print(f">>> {result.message}")
            
            elif option_num == 0:
                print("¡Gracias por jugar!")
                break
            
            else:
                print("Opción no válida")
        
        except ValueError:
            print("Por favor ingresa un número válido")
        except Exception as e:
            print(f"Error inesperado: {e}")
        
        print("-" * 30)