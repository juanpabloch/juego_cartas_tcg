import pdb
from cards import load_cards
from player import Player
from phases import GameState, GamePhase, ActionType

if __name__ == "__main__":
    path = 'control_de_los_mares.csv'
    cards, tresure_cards, token_cards = load_cards(path)
    print(f"Se cargaron {len(cards)} cartas.")

    player_1 = Player("Juan pa", cards.copy(), tresure_cards, token_cards)
    player_1.zones.mazo.shuffle()
    player_1.zones.boveda.shuffle()
    
    player_2 = Player("Ema", cards.copy(), tresure_cards, token_cards)
    player_2.zones.mazo.shuffle()
    player_2.zones.boveda.shuffle()
    
    game_state = GameState(player_1, player_2)
    
    options = {
        "1": "Ver MANO",
        "2": "Ver RESERVA TESOROS",
        "3": "PASAR",
        "0": "Salir"
    }
    
    while not game_state.game_over:
        if game_state.turn_number == 1:
            game_state._start_current_phase()
        
        print("=============================")
        print(f"Turno {game_state.turn_number}")
        print(f"Fase: {game_state.current_phase.value}")
        print("============================= \n")
        
        print("STATE waiting_for_action: ", game_state.waiting_for_action)
        if game_state.waiting_for_action:
            if game_state.waiting_for_action == "mulligan_return":
                if not game_state.players_pending:  # Si no hay jugadores pendientes, continuar
                    continue
                
                print(f"Esperando: {game_state.waiting_for_action}")
                print(f"Jugadores pendientes: {[p.name for p in game_state.players_pending]}")
                
                player = game_state.players_pending[0]
                print("---------")
                print(f"CARTAS {player.name}: ")
                for card in player.zones.hand.see_cards():
                    print(f"{card.name} - {card.text} - Costo: {card.cost} - ID: {card.instance_id}")
                
                print("---------")
                print("\n")
                
                option = int(player.get_player_input(f"{player.name} seleccione una opcion 1 mulligan, 2 seleccionar carta"))
                if option == 1:
                    if player.zones.hand.mulligan_used:
                        continue
                    result = game_state.execute_action(player, ActionType.MULLIGAN_RETURN)
                elif option == 2:
                    card_id = player.get_player_input(f"{player.name} seleccione una carta (ID)")
                    result = game_state.execute_action(player, ActionType.MULLIGAN_RETURN, card_id=card_id)
                
                continue
        
        print("\n=====================")
        for key, value in options.items():
            print(f"{key}: {value}")
        print("===================== \n")
            
        option_num = int(game_state.current_player.get_player_input(f"{game_state.current_player.name} seleccione una opcion"))        

        if option_num == 1:
            print(game_state.current_player.zones.hand.see_cards())
            
        elif option_num == 2:
            print(game_state.current_player.zones.reserva_tesoros.see_cards())
            
        elif option_num == 3:
            # pasar turno o current player
            print("Pasar")
            result = game_state.pass_phase()
            print("RESULT: ", result)
            
        elif option_num == 0:
            print("Gracias por jugar!")
            break
    
        # if game_state.current_phase == GamePhase.SETUP:
        #     if game_state.turn_number == 1:
        #         game_state._start_current_phase()
                
        #     if game_state.waiting_for_action:
        #         print(f"Esperando: {game_state.waiting_for_action}")
        #         print(f"Jugadores pendientes: {[p.name for p in game_state.players_pending]}")
        
        #     # Simular input del jugador
        #     if game_state.waiting_for_action == "mulligan_return":
        #         current_player = game_state.players_pending[0]
        #         print(f"\n>>> {current_player.name}, elegí qué hacer con tu mano inicial:")
        #         print("1. Mulligan (descartar toda la mano y robar 7 nuevas cartas)")
        #         print("2. Retornar 1 carta al fondo del mazo (no hiciste mulligan)")

        #         option_number = int(input("Opción (1/2): "))
        #         card_id = None
        #         if option_number == 1:
        #             result = game_state.execute_action(player_1, ActionType.MULLIGAN_RETURN, card_id=None)
        #             print(result)
        #         elif option_number == 2:
        #             print("CARTAS: ", current_player.zones.hand.see_cards())
        #             card_id = input("¿Qué carta retornás al fondo del mazo?: ")
        #             result = game_state.execute_action(player_1, ActionType.MULLIGAN_RETURN, card_id=card_id)
        #             print(result)
    
    
    # play = True
    
    # options = """
    # 1. Robar 1 carta 
    # 2. robar n cartas 
    # 3. robar tesoro
    # 4. Ver MANO
    # 5. Ver RESERVA
    # 6. Ver FORMACION
    # 7. agotar tesoro id
    # 8. ORO
    # 9. Jugar carta id 
    # 10. Salir
    
    # """
    
    # breakpoint()
    
    # while play:
    #     print(options)
    #     option_number = int(input("Ingresar opcion: "))
    #     if option_number in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
    #         if option_number == 1:
    #             # Robar 1 carta
    #             player_1.actions.draw_card()
                
    #         if option_number == 2:
    #             # robar n cartas
    #             card_count = int(input("Ingresar cantidad de cartas que quieres robar: "))
    #             player_1.actions.draw_card(card_count)
            
    #         if option_number == 3:
    #             # robar carta de tesoro
    #             draw_card = player_1.actions.draw_treasure()
                
    #         if option_number == 4:
    #             # Ver MANO
    #             print(f"Mazo: {player_1.zones.mazo.__len__()}")
    #             print(f"{len(player_1.zones.hand.cards)} CARTAS")
    #             print(player_1.zones.hand.see_cards())

    #         if option_number == 5:
    #             # Ver RESERVA
    #             print(f"Tesoros: {player_1.zones.boveda.__len__()}")
    #             print(f"{len(player_1.zones.reserva_tesoros)} CARTAS")
    #             print(player_1.zones.reserva_tesoros.see_cards())
                
    #         if option_number == 6:
    #             # Ver FORMACION
    #             print(f"{len(player_1.zones.formacion)} CARTAS")
    #             print(player_1.zones.formacion.see_cards())
                
            
    #         if option_number == 7:
    #             # agotar tesoro id
    #             card_id = input("Ingresar id del tesoro a agotar: ")
    #             result = player_1.actions.agotar_tesoro(card_id)
    #             if result:
    #                 print(f"Cantidad de oro: {player_1.resources.available_gold}")
                
    #         if option_number == 8:
    #             # Cantidad de ORO
    #             print("Cantidad de ORO generado: ", player_1.resources.available_gold)
                
    #         if option_number == 9:
    #             # Jugar carta
    #             card_id = input("Ingresar id de la carta a Jugar: ")
    #             result = player_1.actions.play_card(card_id)
    #             if result:
    #                 print("Carta jugada")
    #             else:
    #                 print("No se puede juagar la carta")

    #         if option_number == 10:
    #             # Salir
    #             print("Gracias por jugar!")
    #             play = False



