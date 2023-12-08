import sqlite3
import time
import os

def valida_cpf(cpf):
  # Verifica se o CPF tem 11 dígitos
  if len(cpf) != 11:
    return False

  # Verifica se todos os dígitos são iguais
  if cpf == cpf[0] * 11:
    return False

  # Verifica o primeiro dígito verificador
  soma = 0
  for i in range(9):
    soma += int(cpf[i]) * (10 - i)
  resto = soma % 11
  if resto < 2:
    digito1 = 0
  else:
    digito1 = 11 - resto
  if digito1 != int(cpf[9]):
    return False

  # Verifica o segundo dígito verificador
  soma = 0
  for i in range(10):
    soma += int(cpf[i]) * (11 - i)
  resto = soma % 11
  if resto < 2:
    digito2 = 0
  else:
    digito2 = 11 - resto
  if digito2 != int(cpf[10]):
    return False

  # Se passou por todas as verificações, o CPF é válido
  return True

class Banco:
    def __init__(self):
        self.conn = sqlite3.connect("banco.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(50),
            cpf VARCHAR(11),
            saldo DECIMAL(10, 2),
            cargo VARCHAR(20),
            senha VARCHAR(50)
        );
        ''')
        self.conn.commit()
        self.cargo_atual = "cliente"
        self.transferencias_programadas = {}
        self.Chave_definida =  "Calopsitasehvida123"
        self.contas = {}
        self.reclamacoes = {}


    def transferir(self, origem_cpf, destino_cpf, valor, tipo_transferencia):
        if not self.verificar_existencia_usuario(origem_cpf) or not self.verificar_existencia_usuario(destino_cpf):
            print("CPF de origem ou destino não encontrado. A transferência não pode ser realizada.")
            return

        if tipo_transferencia == "pix":
            if self.sacar(origem_cpf, valor):
                self.adicionar_saldo(destino_cpf, valor)
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Transferência PIX de R${valor:.2f} realizada com sucesso.")
                os.system("cls")
        elif tipo_transferencia == "ted":
            if origem_cpf not in self.transferencias_programadas:
                self.transferencias_programadas[origem_cpf] = {}
            self.transferencias_programadas[origem_cpf][destino_cpf] = valor
            for i in range(1, 11):
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Transferência TED de R${valor:.2f} programada para ser realizada em {10-i}s")
                time.sleep(1)
            print("Transferencia realizada com sucesso!")
            os.system("pause")
            os.system("cls")
            if origem_cpf in self.transferencias_programadas and destino_cpf in self.transferencias_programadas[origem_cpf]:
                valor_ted = self.transferencias_programadas[origem_cpf].pop(destino_cpf)
                if self.sacar(origem_cpf, valor_ted):
                    self.adicionar_saldo(destino_cpf, valor_ted)
                    os.system('cls')
                    print("-"*20, "Banco Seguro S/A", "-"*20)
                    print(f"Transferência TED de R${valor_ted:.2f} realizada com sucesso.")
                    os.system("pause")
                    os.system("cls")

    def sacar(self, cpf_saque, valor_saque):
        if self.verificar_existencia_usuario(cpf_saque):
            if self.verificar_saldo_suficiente(cpf_saque, valor_saque):
                self.cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE cpf = ?", (valor_saque, cpf_saque))
                return True
            else:
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print("Saldo insuficiente para realizar o saque. ")
                os.system("pause")
                os.system("cls")
        else:
            os.system('cls')
            print("-"*20, "Banco Seguro S/A", "-"*20)
            print(f"Usuário com CPF {cpf_saque} não encontrado.")
            os.system("pause")
            os.system("cls")
        return False

    def adicionar_usuario(self, nome, cpf, senha):
        if not self.verificar_existencia_usuario(cpf):
            self.cursor.execute("INSERT INTO usuarios (nome, cpf, saldo, cargo, senha) VALUES (?, ?, ?, ?, ?)",
                                (nome, cpf, 0.0, self.cargo_atual, senha))
            self.conn.commit()
            print("Conta criada com sucesso!")
        else:
            print("CPF já está em uso. Não é possível adicionar o usuário.")

    def consultar_saldo(self, cpf_consulta):
        if self.verificar_existencia_usuario(cpf_consulta):
            print("-"*20, "Banco Seguro S/A", "-"*20)
            senha = input("Digite a senha: ")
            if self.verificar_senha(cpf_consulta, senha):
                self.cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf_consulta,))
                resultado = self.cursor.fetchone()
                saldo = resultado[0]
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Saldo do usuário com CPF {cpf_consulta}: R${saldo:.2f}")
                os.system("pause")
                os.system('cls')
            else:
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print("Senha incorreta.")
                os.system("pause")
                os.system('cls')
        else:
            print("-"*20, "Banco Seguro S/A", "-"*20)
            print(f"Usuário com CPF {cpf_consulta} não encontrado.")
            os.system("pause")
            os.system('cls')
            


    def adicionar_saldo(self, cpf_adicao, valor_adicao):
        if self.verificar_existencia_usuario(cpf_adicao):
            self.cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE cpf = ?", (valor_adicao, cpf_adicao))
            self.conn.commit()
            
        else:
            os.system('cls')
            print("-"*20, "Banco Seguro S/A", "-"*20)
            print(f"Usuário com CPF {cpf_adicao} não encontrado.")
            os.system("pause")
            os.system('cls')

    def excluir_usuario(self, cpf_exclusao):
        if self.verificar_existencia_usuario(cpf_exclusao):
            saldo_cpf_exclusao = self.obter_saldo(cpf_exclusao)

            if saldo_cpf_exclusao > 0:
                print(f"Saldo em conta. Por favor, retire o dinheiro antes de excluir a conta. Saldo atual: R${saldo_cpf_exclusao:.2f}")
            else:
                confirmacao = input("Tem certeza que deseja excluir este usuário? (S/N): ").strip().lower()
                if confirmacao == 's':
                    self.cursor.execute("DELETE FROM usuarios WHERE cpf = ?", (cpf_exclusao,))
                    self.conn.commit()
                    print(f"Usuário com CPF {cpf_exclusao} foi excluído com sucesso.")
                else:
                    print("Exclusão cancelada.")
        else:
            print(f"Usuário com CPF {cpf_exclusao} não encontrado.")

    def verificar_existencia_usuario(self, cpf):
        self.cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
        resultado = self.cursor.fetchone()
        return resultado is not None

    def verificar_saldo_suficiente(self, cpf, valor):
        self.cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf,))
        resultado = self.cursor.fetchone()
        if resultado:
            saldo = resultado[0]
            return saldo >= valor
        return False

    def obter_saldo(self, cpf):
        self.cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf,))
        resultado = self.cursor.fetchone()
        if resultado:
            return resultado[0]
        return 0.0

    def verificar_senha(self, cpf, senha):
        self.cursor.execute("SELECT senha FROM usuarios WHERE cpf = ?", (cpf,))
        resultado = self.cursor.fetchone()
        if resultado:
            senha_armazenada = resultado[0]
            return senha == senha_armazenada
        return False

    def realizar_pagamento(self, cpf, valor, tipo_conta):
        if self.verificar_existencia_usuario(cpf):
            if self.verificar_saldo_suficiente(cpf, valor):
                self.cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE cpf = ?", (valor, cpf))
                self.conn.commit()
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Pagamento de conta de {tipo_conta} no valor de R${valor:.2f} realizado com sucesso.")
                os.system("pause")
                os.system("cls")
            else:
                print("\nSaldo insuficiente para realizar o pagamento.")
                os.system("pause")
                os.system("cls")
        else:
            print(f"\nUsuário com CPF {cpf} não encontrado.")
            os.system("pause")
            os.system("cls")

    def adicionar_conta(self, cpf, saldo_inicial):
      if cpf not in self.contas:
          self.contas[cpf] = saldo_inicial
          print(f"Conta com CPF {cpf} criada com saldo inicial de R${saldo_inicial:.2f}")
      else:
          print("CPF já está em uso. Não é possível adicionar a conta.")

    def Chave_de_acesso(self):
      return self.Chave_definida
      
    def Mudar_Chave(self, Alteracao_de_Chave):
      self.Alteracao_de_Chave = Alteracao_de_Chave
      print("Chave alterada com sucesso!")

    def exibir_menu(self):
        while True:
            os.system("cls")
            print("-"*20, "Banco Seguro S/A", "-"*20)
            print("\nBem Vindo ao menu digital!")
            print("-" *20)
            print(
            "1. Criar Cadastro\
            \n2. Extrato Bancário\
            \n3. Depositar\
            \n4. Sacar saldo\
            \n5. Transferência PIX\
            \n6. Transferência TED\
            \n7. Realizar Pagamento\
            \n8. Reclame aqui\
            \n9. Menu Administrativo\
            \n10. Sair")
            print("-" *20)
            
            opcao = input("\nDigite uma opção: ")
            os.system('cls')

            if opcao == "1":
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                nome = input("Digite o nome do usuário: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                cpf = input("Digite o CPF do usuário: ")
                if valida_cpf(cpf):
                    print("Validando CPF...")
                    print("CPF validado com sucesso.\n")

                else:
                    while True:
                        cpf = input("CPF inválido! Tente novamente: ")
                        os.system('cls')

                        if valida_cpf(cpf):
                           break
                
                senha = input("Digite a senha: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                confirma_senha = input("Confirme a senha: ")
                os.system('cls')
                
                while senha != confirma_senha:
                    os.system('cls')
                    print("-"*20, "Banco Seguro S/A", "-"*20)
                    print("As senhas digitadas não coincidem. Por favor, tente novamente: ")
                    senha = input("Digite a senha: ")
                    os.system('cls')
                    print("-"*20, "Banco Seguro S/A", "-"*20)
                    confirma_senha = input("Confirme a senha: ")
                if senha == confirma_senha:
                    self.adicionar_usuario(nome, cpf, senha)
                    os.system("pause")
                    os.system('cls')
 

            elif opcao == "2":
                print("-"*20, "Banco Seguro S/A", "-"*20)
                cpf_consulta = input("Digite o CPF do usuário para consultar o saldo: ")
                os.system('cls')
                self.consultar_saldo(cpf_consulta)


            elif opcao == "3":
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                cpf_deposito = input("Digite o CPF do usuário para depositar: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                valor_deposito = float(input("Digite o valor a ser depositado: R$"))
                self.adicionar_saldo(cpf_deposito, valor_deposito)
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Saldo atualizado com sucesso. Deposito: R${valor_deposito:.2f}")
                os.system("pause")
                os.system('cls')

            elif opcao == "4":
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                cpf_saque = input("Digite o CPF do usuário para sacar: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                valor_saque = float(input("Digite o valor a ser sacado: R$"))
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                print(f"Saque de R${valor_saque:.2f} realizado com sucesso.")
                os.system("pause")
                os.system("cls")
                self.sacar(cpf_saque, valor_saque)

            elif opcao == "5":
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                origem_cpf = input("Digite o CPF de origem da transferência: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                destino_cpf = input("Digite o CPF de destino da transferência: ")
                os.system('cls')
                print("-"*20, "Banco Seguro S/A", "-"*20)
                valor_transferencia = float(input("Digite o valor a ser transferido: R$"))
                self.transferir(origem_cpf, destino_cpf, valor_transferencia, "pix")



            elif opcao == "6":
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                origem_cpf = input("Digite o CPF de origem da transferência: ")
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                destino_cpf = input("Digite o CPF de destino da transferência: ")
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                valor_transferencia = float(input("Digite o valor a ser transferido: R$"))
                self.transferir(origem_cpf, destino_cpf, valor_transferencia, "ted")
                os.system("pause")
                os.system("cls")
    

            elif opcao == "7":
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                cpf_pagamento = input("Digite o CPF do usuário para realizar o pagamento: ")
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                valor_pagamento = float(input("Digite o valor da conta: R$"))
                os.system("cls")
                print("-"*20, "Banco Seguro S/A", "-"*20)
                tipo_conta = input("Descreva o pagamento: ")
                self.realizar_pagamento(cpf_pagamento, valor_pagamento, tipo_conta)

            elif opcao == "8":
                print("Reclame aqui")
                reclamação = input("Nos exclareça sua reclamação:")
                self.reclamacoes[reclamação] = True
                print("Seu problema chegou até o Administrador, estamos trabalhando para corrigir o erro!")
            
            elif opcao == "9":
                os.system('cls')
                print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                Chave_acesso=input("Digite a Chave de Acesso: ")
                while Chave_acesso != self.Chave_definida:
                    os.system("cls")
                    print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                    print("Chave inválida!")
                    Chave_acesso=input("Digite a Chave de Acesso: ")
                if Chave_acesso == self.Chave_definida:
                    os.system("cls")
                    print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                    print("Acesso Liberado!")
                    time.sleep(3)
                    os.system("cls")

                while True:
                    print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                    print(
                    "\n1. Reclame aqui \
                    \n2. Boas práticas\
                    \n3. Excluir cadastro\
                    \n4. Sair")
                  
                    opcao = input("\nDigite uma opção: ")

                    if opcao == "1":
                            os.system("cls")
                            print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                            print("Feedbacks: ")
                            print(self.reclamacoes)
                            os.system("pause")
                            os.system("cls")

                    elif opcao == "2":
                            os.system("cls")
                            print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                            print("Regras do Banco:\n")
                            print("Ao adotar boas práticas de governança corporativa,\
                                \no Banco Seguro - Triangulo, demonstra que sua administração se compromete\
                                \ncom os princípios básicos de Transparência, Prestação de Contas,\
                                \nEquidade e Responsabilidade Socioambiental, suportadas pela utilização de\
                                \nferramentas de monitoramento que alinham o comportamento dos administradores\
                                \nao interesse dos acionistas, dos clientes e da sociedade.\n")
                            os.system("pause")
                            os.system("cls")

                            

                    elif opcao == "3":
                        os.system("cls")
                        print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                        cpf_exclusao = input("Digite o CPF do usuário para excluir: ")
                        print("\n")
                        self.excluir_usuario(cpf_exclusao)
                        print("\n")
                        os.system("pause")
                        os.system("cls")

                    
                    elif opcao  == "4":
                            os.system("cls")
                            print("-"*20, "Banco Seguro S/A - MENU ADMINISTRATIVO", "-"*20)
                            print("Saindo do menu Administrativo.")
                            time.sleep(3)
                            break
                    else:
                        os.system("cls")
                        print("Opção inválida!")
                        os.system("pause")

            elif opcao == "10":
                print("Obrigado por escolher o Banco Seguro - Triangulo. Volte sempre!")
                break
            else:
              os.system("cls")
              print("Opção inválida!")
              os.system("pause")

if __name__ == "__main__":
  banco = Banco()
  banco.exibir_menu()