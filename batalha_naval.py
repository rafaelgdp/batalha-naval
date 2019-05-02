# Estruturando o programa da batalha naval.
# @author Rafael Pontes
# Maio, 2019

import pygame
import os
import time
import math
from enum import Enum
import spritesheet

WHITE = (255,250,250)
BLACK = (0,0,0)

#Navio de batalha
class Embarcacao():

    class EstadoCelula(Enum):
        OCULTA = 0
        DESTRUIDA = 1
        VISIVEL = 2

    # Construtor
    def __init__(self, posicao, tamanho, sentido):
        self.posicao = posicao
        self.tamanho = tamanho
        self.sentido = sentido

        self.estados_celulas = list()
        for indice_celula in range(tamanho):
            self.estados_celulas.append(Embarcacao.EstadoCelula.VISIVEL)
    
    def tornar_invisivel(self):
        for indice_celula in range(self.tamanho):
            self.estados_celulas[indice_celula] = Embarcacao.EstadoCelula.OCULTA

    def atacar_celula(self, posicao, dimensao_celula):
        if (self.sentido == "H"):
            salto_horizontal = dimensao_celula[0]
            for index_celula in range(self.tamanho):
                x_atual = (index_celula * salto_horizontal) + self.posicao[0]
                if self.posicao[1] == posicao[1] and x_atual == posicao[0]:
                    self.estados_celulas[index_celula] = Embarcacao.EstadoCelula.DESTRUIDA

    def ocupa_celula(self, posicao, dimensao_celula):
        if (self.sentido == "H"):
            salto_horizontal = dimensao_celula[0]
            for index_celula in range(self.tamanho):
                x_atual = (index_celula * salto_horizontal) + self.posicao[0]
                if self.posicao[1] == posicao[1] and x_atual == posicao[0]:
                    return True
        return False
    
    def get_destruidas(self):
        destruidas = 0
        for estado in self.estados_celulas:
            if (estado == Embarcacao.EstadoCelula.DESTRUIDA):
                destruidas += 1
        return destruidas

class Jogador():
    def __init__(self, id):
        self.embarcacoes = list()
        self.hits_marinhos = list()

    def adicionar_embarcacao(self, embarcacao):
        self.embarcacoes.append(embarcacao)

    def get_embarcacoes(self):
        return self.embarcacoes
    
    def adicionar_hit_marinho(self, posicao):
        self.hits_marinhos.append(posicao)

    def atacar_posicao(self, posicao, dimensao_celula):
        if (self.eh_mar(posicao, dimensao_celula)):
            self.adicionar_hit_marinho(posicao)
        else:
            for i in range(len(self.embarcacoes)):
                self.embarcacoes[i].atacar_celula(posicao, dimensao_celula)
    
    def get_destruidas(self):
        destruidas = 0
        for embarcacao in self.embarcacoes:
            destruidas += embarcacao.get_destruidas()
        return destruidas
    
    def eh_mar(self, posicao, dimensao):
        for embarcacao in self.embarcacoes:
            if (embarcacao.ocupa_celula(posicao, dimensao)):
                return False
        return True

class Game():

    class State(Enum):
        """
            INICIO é a parte do jogo onde cada jogador coloca suas embarcações
            no seu respectivo tabuleiro
        """
        INICIO_JOGADOR_1 = 0
        INICIO_JOGADOR_2 = 1

        # Fim da inicialização
        FIM_INICIALIZACAO = 6

        """
            VEZ é a parte principal da partida, onde cada jogador escolhe uma
            célula do tabuleiro inimigo para atacar
        """
        VEZ_JOGADOR_1 = 2
        VEZ_JOGADOR_2 = 3

        """
            VITORIA é a parte final da partida, na qual algum dos dois jogadores
            destruiu todas as embarcações do inimigo
        """
        VITORIA_JOGADOR_1 = 4
        VITORIA_JOGADOR_2 = 5

    def __init__(self,
                 tamanho_horizontal_cada_tabuleiro,
                 tamanho_vertical_cada_tabuleiro):

        self.MAXIMO_EMBARCACOES = 5
        self.celulas_por_jogador = self.MAXIMO_EMBARCACOES * 3

        # Jogadores
        self.jogador_1 = Jogador(1)
        self.jogador_2 = Jogador(2)

        # Variável que indica o estado atual do jogo
        self.estado_jogo = Game.State.INICIO_JOGADOR_1

        # Ajustando as variáveis relacionadas com a tela e inicialização do pygame
        self.qnt_celulas_x_cada_tabuleiro = tamanho_horizontal_cada_tabuleiro
        self.qnt_celulas_y_cada_tabuleiro = tamanho_vertical_cada_tabuleiro
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption('Batalha Naval - By Rafael Pontes')
        self.margin = 20 # Margens laterais
        self.cell_size = 20  + 1 # Tamanho de cada celula (quadradinho da matriz)

        # Definindo o tamanho horizontal da tela do jogo:
        # 1) Tem que comportar células dos DOIS tabuleiros
        tamanho_horizontal_tela = self.qnt_celulas_x_cada_tabuleiro * self.cell_size * 2
        # 2) Adicionando um pixel para seperar visualmente as células dos DOIS tabuleiros:
        tamanho_horizontal_tela += self.qnt_celulas_x_cada_tabuleiro * 1 * 2
        # 3) Adicionando espaço para a margem esquerda e direita:
        tamanho_horizontal_tela += 2 * self.margin

        # Definindo o tamanho vertical da tela do jogo:
        # 1) Tem que comportar células verticais apenas em relação a um tabuleiro:
        tamanho_vertical_tela = self.qnt_celulas_y_cada_tabuleiro * self.cell_size
        # 2) Adicionando um pixel para seperar as células visualmente:
        tamanho_vertical_tela += self.qnt_celulas_x_cada_tabuleiro * 1
        # 3) Adicionando espaço para a margem superior e inferior:
        tamanho_vertical_tela += 2 * self.margin

        self.screen_size = (tamanho_horizontal_tela, tamanho_vertical_tela)
        self.board = pygame.display.set_mode(self.screen_size)

        # Carregando as imagens do spritesheet criado até agora
        ss = spritesheet.spritesheet('battle_ship_sprites.png')
        self.SEA_SPRITE = ss.image_at((0, 0, 20, 20)) # Imagem do mar sem nada
        self.BARCOS = [] # Imagens das três celulas das embarcações horizontais
        # Load two images into an array, their transparent bit is (255, 255, 255)
        self.BARCOS = ss.images_at([
            (20, 0, 20, 20),  # Celula esquerda
            (40, 0, 20, 20),  # Celula centro
            (60, 0, 20, 20)])  # Celula direita
        self.DESTRUIDA = ss.image_at((80, 0, 20, 20))
        self.HIT_MARINHO = ss.image_at((100, 0, 20, 20))

    def clear_screen(self):
        """
            Função que limpa os pixels da tela na memória para exibir apenas o
            mar com o tabuleiro vazio (Não imprime na tela ainda, pois outras
            funções vão definir os elementos do jogo, como embarcações abatidas,
            tiros errados etc). Ao final de todas as chamadas de funções
            visuais, o jogo é finalmente impresso na tela. Isso evita glitches
            em computadores mais lentos, pois toda a informação da tela é
            impressa de uma única vez.
        """
        self.board.fill(BLACK) # Cor de fundo
        quantos = 0
        for x in range(self.margin + 1, self.screen_size[0] - self.margin, self.cell_size):
            for y in range(self.margin + 1, self.screen_size[1] - self.margin, self.cell_size):
                # Desenhando as células do mar
                self.board.blit(self.SEA_SPRITE, (x, y))

        central_line = [(self.screen_size[0]//2, 0),  # Ponto inicial
                        (self.screen_size[0]//2, self.screen_size[1])]  # Ponto final
        pygame.draw.line(self.board, (255, 0, 0), central_line[0], central_line[1], 2)

    def celula_por_posicao(self, posicao):
        x = (posicao[0] - self.margin) // (self.cell_size)
        y = (posicao[1] - self.margin) // (self.cell_size)
        x = self.margin + 1 + x * (self.cell_size)
        y = self.margin + 1 + y * (self.cell_size)
        return (x, y)

    def indice_tabuleiro_jogador_por_posicao(self, posicao):
        """
            Retorna um índice referente à célula da matriz do tabuleiro.
            Mapeia o índice para uma posição da matriz do jogo.
            Tipicamente, para um tabuleiro 20x20, o retorno é uma 2-tupla
            da forma: (i, j), 0 <= i, j <= 19.
        """
        area_jogador_1 = pygame.Rect(
                        self.margin + 1,
                        self.margin + 1,
                        self.cell_size * self.qnt_celulas_x_cada_tabuleiro,
                        self.cell_size * self.qnt_celulas_y_cada_tabuleiro)

        area_jogador_2 = pygame.Rect(
                        (self.screen_size[0] // 2) + 1,
                        self.margin + 1,
                        self.cell_size * self.qnt_celulas_x_cada_tabuleiro,
                        self.cell_size * self.qnt_celulas_y_cada_tabuleiro)

        celula_global = self.celula_por_posicao(posicao)
        if (area_jogador_1.collidepoint(posicao)):
            # Clicou na regiao do jogador 1
            x = (celula_global[0] - self.margin) // self.cell_size
            y = (celula_global[1] - self.margin) // self.cell_size
            return (x, y)
        elif (area_jogador_2.collidepoint(posicao)):
            # Clicou na regiao do jogador 2
            x = (celula_global[0] - self.margin) // self.cell_size
            y = (celula_global[1] - self.margin) // self.cell_size
            x -= 20
            return (x, y)
        else:
            # Região não pertence a nenhum dos tabuleiros
            return None
            pass

    def draw_celula_embarcacao(self, embarcacao, celula):
        if (embarcacao.estados_celulas[celula] == Embarcacao.EstadoCelula.VISIVEL):
            pos_atual = (embarcacao.posicao[0] +
                         (celula * self.cell_size), embarcacao.posicao[1])
            imagem = None
            if (celula == 0):
                imagem = self.BARCOS[celula]
            elif (celula < (embarcacao.tamanho - 1)):
                imagem = self.BARCOS[1]
            else:
                imagem = self.BARCOS[2]
            self.board.blit(imagem, pos_atual)
        elif (embarcacao.estados_celulas[celula] == Embarcacao.EstadoCelula.OCULTA):
            pos_atual = (embarcacao.posicao[0] +
                         (celula * self.cell_size), embarcacao.posicao[1])
            self.board.blit(self.SEA_SPRITE, pos_atual)
        elif (embarcacao.estados_celulas[celula] == Embarcacao.EstadoCelula.DESTRUIDA):
            pos_atual = (embarcacao.posicao[0] +
                         (celula * self.cell_size), embarcacao.posicao[1])
            self.board.blit(self.DESTRUIDA, pos_atual)
        

    def draw_embarcacao(self, embarcacao):
        for celula in range(embarcacao.tamanho):
            self.draw_celula_embarcacao(embarcacao, celula)

    def draw_embarcacoes(self, barcos):
        for barco in barcos:
            self.draw_embarcacao(barco)

    def draw_hits_marinhos(self, posicoes):
        for posicao in posicoes:
            self.board.blit(self.HIT_MARINHO, posicao)

    def reagir_a_clique(self, posicao_clique):
        if (self.estado_jogo == Game.State.INICIO_JOGADOR_1):
            if (len(self.jogador_1.get_embarcacoes()) >= self.MAXIMO_EMBARCACOES):
                self.estado_jogo = Game.State.INICIO_JOGADOR_2
            else:
                regiao_clicavel = pygame.Rect(
                            self.margin + 1,
                            self.margin + 1,
                            self.cell_size * 19 - 1,
                            self.cell_size * 21 - 1)
                if (regiao_clicavel.collidepoint(posicao_clique)):
                    nova_embarcacao = Embarcacao(
                        self.celula_por_posicao(posicao_clique), 3, "H")
                    self.jogador_1.adicionar_embarcacao(nova_embarcacao)
        elif (self.estado_jogo == Game.State.INICIO_JOGADOR_2):
            if (len(self.jogador_2.get_embarcacoes()) >= self.MAXIMO_EMBARCACOES):
                self.estado_jogo = Game.State.FIM_INICIALIZACAO
            else:
                regiao_clicavel = pygame.Rect(
                    self.screen_size[0] // 2 + 1,
                    self.margin + 1,
                    self.cell_size * 19 - 1,
                    self.cell_size * 21 - 1)
                if (regiao_clicavel.collidepoint(posicao_clique)):
                    nova_embarcacao = Embarcacao(
                        self.celula_por_posicao(posicao_clique), 3, "H")
                    self.jogador_2.adicionar_embarcacao(nova_embarcacao)
        elif (self.estado_jogo == Game.State.VEZ_JOGADOR_1):
            regiao_clicavel = pygame.Rect(
                self.screen_size[0] // 2 + 1,
                self.margin + 1,
                self.cell_size * 21 - 1,
                self.cell_size * 21 - 1)
            if (regiao_clicavel.collidepoint(posicao_clique)):
                dimensao_celula = (self.cell_size, self.cell_size)
                self.jogador_2.atacar_posicao(
                    self.celula_por_posicao(posicao_clique), dimensao_celula)
                self.estado_jogo = Game.State.VEZ_JOGADOR_2
                if self.jogador_2.get_destruidas() >= self.celulas_por_jogador:
                    self.estado_jogo = Game.State.VITORIA_JOGADOR_1
        elif (self.estado_jogo == Game.State.VEZ_JOGADOR_2):
            regiao_clicavel = pygame.Rect(
                    self.margin + 1,
                    self.margin + 1,
                    self.cell_size * 21 - 1,
                    self.cell_size * 21 - 1)
            if (regiao_clicavel.collidepoint(posicao_clique)):
                dimensao_celula = (self.cell_size, self.cell_size)
                self.jogador_1.atacar_posicao(
                    self.celula_por_posicao(posicao_clique), dimensao_celula)
                self.estado_jogo = Game.State.VEZ_JOGADOR_1
                if self.jogador_1.get_destruidas() >= self.celulas_por_jogador:
                    self.estado_jogo = Game.State.VITORIA_JOGADOR_2

    def imprime_mensagem_tela(self, mensagem):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(mensagem, True, BLACK, WHITE)
        textRect = text.get_rect()
        textRect.center = (self.screen_size[0] // 2, self.screen_size[1] // 2)
        self.board.blit(text, textRect)


    def imprime_hint_tela(self, mensagem):
            font = pygame.font.Font('freesansbold.ttf', 20)
            text = font.render(mensagem, True, BLACK, WHITE)
            textRect = text.get_rect()
            textRect.center = (self.screen_size[0] // 2, self.margin // 2)
            self.board.blit(text, textRect)

    def update_celulas_embarcacoes(self):
        if (self.estado_jogo == Game.State.INICIO_JOGADOR_2):
            for indice_embarcacao in range(len(self.jogador_1.get_embarcacoes())):
                self.jogador_1.embarcacoes[indice_embarcacao].tornar_invisivel()
        elif (self.estado_jogo == Game.State.FIM_INICIALIZACAO):
            for indice_embarcacao in range(len(self.jogador_2.get_embarcacoes())):
                self.jogador_2.embarcacoes[indice_embarcacao].tornar_invisivel()
            self.estado_jogo = Game.State.VEZ_JOGADOR_1
        elif (self.estado_jogo == Game.State.VITORIA_JOGADOR_1):
            self.imprime_mensagem_tela("Jogador 1 ganhou!")
        elif (self.estado_jogo == Game.State.VITORIA_JOGADOR_2):
            self.imprime_mensagem_tela("Jogador 2 ganhou!")
            
    def main_game_loop(self):
        leave = False
        while leave == False:
            self.clear_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    leave = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.reagir_a_clique(pygame.mouse.get_pos())
            self.update_celulas_embarcacoes()
            self.draw_embarcacoes(self.jogador_1.get_embarcacoes())
            self.draw_embarcacoes(self.jogador_2.get_embarcacoes())
            if (self.estado_jogo == Game.State.VEZ_JOGADOR_1):
                self.imprime_hint_tela("Agora é a vez do jogador 1.")
            elif (self.estado_jogo == Game.State.VEZ_JOGADOR_2):
                self.imprime_hint_tela("Agora é a vez do jogador 2.")
            elif (self.estado_jogo == Game.State.INICIO_JOGADOR_1):
                self.imprime_hint_tela("Vez do jogador 1 colocar os navios.")
            elif (self.estado_jogo == Game.State.INICIO_JOGADOR_2):
                self.imprime_hint_tela("Vez do jogador 2 colocar os navios.")
            self.draw_hits_marinhos(self.jogador_1.hits_marinhos)
            self.draw_hits_marinhos(self.jogador_2.hits_marinhos)
            pygame.display.update()

if __name__ == "__main__":
    game = Game(20, 20)
    game.clear_screen()
    game.main_game_loop() # Chamada bloqueante
    pygame.quit() # Só chega aqui quando o game_loop acaba
