# Paulina Vara Figueroa 2020
# Este programa pretende implementar algoritmos evolutivos en el problema del vendedor viajero
# Se hace una combinación entre algoritmos genéticos y estrategias evolutivas:
#  - Ocupa ruleta para la selección de datos en el crossover
#  - Entre la población atual y los nuevos individuos generados se hace una selección, dato por dato ocurre:
#     - Se toma el mejor y un dato aleatorio, el mejor tiene 60% de probabilidad de ser seleccionado para pasar
# La interfaz permite:
#  - Crear un mapa seleccionando los puntos directamente
#  - Guardar un mapa creado
#  - Cargar un mapa desde archivo (.txt)
#  - Elegir si hay un punto de inicio fijo o no
#  - Repetir la búsqueda sobre el mismo mapa
import matplotlib.pyplot as plt
import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) # Unir plot a ventana tkinter
from tkinter import messagebox as msb
from tkinter.filedialog import asksaveasfile

import math
import random

global coordenadas  # Puntos a considerar en la ruta, si pide punto de partida se considera el de la posición 0

def cargarArchivo(ven_Anterior, respetarPrimero): # Lee archivo en 2 listas: 1 de coordenadas X, y una de coordenadas Y
    global coordenadas
    coordenadas = []
    archivo = tkinter.filedialog.askopenfile(title="Select file",
                                             filetypes=(("text files", "*.txt"), ("all files", "*.*")))
    if archivo is not None:
        mapaCoordenadas = archivo.readlines() # Lo lee por líneas, cada coordenada está una línea
        for coordenada in mapaCoordenadas:
            splitCoord = coordenada.split(" ")
            splitCoord.pop() # Saca al caracter '\n' para tener solo x & y
            coordenadas.append(list(map(float, splitCoord)))
        buscarCostoMinimo(ven_Anterior, respetarPrimero) # En cuanto lee el archivo, abre la ventana de búsqueda

def buscarCostoMinimo(ven_Anterior, respetarPrimero): # Aquí se ejecuta el algoritmo de aprendizaje
    global coordenadas
    global lb_costoMin, lb_puntoPartida, lb_cruzaMut, b_buscar, lb_iteraciones # Las etiquetas y botón se hacen
                                                    # globales a la función para modificar su texto cuando necesario
    global mutacion # Se maneja así para poder ir mostrando su valor cuando cambia
    # Funciones a utilizar en esta ventana:
    def dibujarRuta(ruta, costo):
        # Limpia el plot (por si ya había trazado una ruta)
        ax.clear()
        # Vuelve a darle formato y dibujar los puntos:
        formatoDePlot()
        plt.grid()
        esPrimeraCoordenada = True
        for punto in ruta:
            if (esPrimeraCoordenada):
                plt.plot(coordenadas[punto][0], coordenadas[punto][1], 'rX')
                esPrimeraCoordenada = False
            else:
                plt.plot(coordenadas[punto][0], coordenadas[punto][1], 'o')
        fig.canvas.draw()
        # Indica el que se está considerando como punto de partida y el costo de la ruta que dibuja:
        lb_puntoPartida.configure(
            text=('(' + str(coordenadas[ruta[0]][0]) + ' , ' + str(coordenadas[ruta[0]][1]) + ')'))
        lb_costoMin.configure(text=str(round(costo, 3)))
        rCruza = round(1-mutacion,2)
        rMut = round(mutacion,2)
        lb_cruzaMut.configure(text=' - Rango de cruza = '+str(rCruza)+'\n - Rango de mutación = '+str(rMut))
        # Dibuja la ruta:
        i = 0
        while (i < len(ruta) - 1): # '-1' porque la ultima línea debe ir del último al primero, no entra en este ciclo
            x_values = [coordenadas[ruta[i]][0], coordenadas[ruta[i + 1]][0]]
            y_values = [coordenadas[ruta[i]][1], coordenadas[ruta[i + 1]][1]]
            plt.plot(x_values, y_values, color='black')
            i += 1
        # Dibuja la última línea, del último punto al primero
        x_values = [coordenadas[ruta[i]][0], coordenadas[ruta[0]][0]]
        y_values = [coordenadas[ruta[i]][1], coordenadas[ruta[0]][1]]
        plt.plot(x_values, y_values, color='black')
        fig.canvas.draw()

    def formatoDePlot():
        # Le da formato al título del plot
        ax.set_title("MAPA", fontsize='large', color='black', weight='bold')
        # Le da formato a las etiquetas de los ejes del plot
        for tick in ax.xaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')
        for tick in ax.yaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')

    def iniciarBusqueda(): # Inicia algoritmo de aprendizaje
        global mutacion # Para que pueda irse mostrando su valor en la función "dibujarRuta()"
        global lb_iteraciones # Para mostrar el total de iteraciones al finalizar la bpusqueda
        b_buscar.configure(state=tkinter.DISABLED) # Durante la búsqueda se desactiva el botón de buscar

        def mezclarLista(listaParaMezclar, respetarPrimero):  # Devuelve la lista ya mezclada
            # respetarPrimero si es True no cambia el valor del dato en posición 0 si es False, si lo mezcla
            # Se usa el algoritmo Fisher–Yates para mezclar los elementos de la lista aleatoriamente
            for i in range(len(listaParaMezclar) - 1, 0, -1):
                if (respetarPrimero):
                    # Se busca una posición aleatoria para cambio a partir del dato en el índice 1
                    j = random.randint(1, i)
                else:
                    # Se busca una posición aleatoria para cambio a partir del dato en el índice 0
                    j = random.randint(0, i)
                # Se cambia el dato
                listaParaMezclar[i], listaParaMezclar[j] = listaParaMezclar[j], listaParaMezclar[i]
            return listaParaMezclar

        def crearNuevaPoblacion(poblacion, mutacion, n_NuevasRutas, respetarPrimero, fitness): # Devuelve nuevaPoblacion
            # Primero se eligen los n individuos de cruza para evitar errores, ya que se necesita un número par
            cruza = 1 - mutacion
            n_rutasCruzar = math.ceil(n_NuevasRutas * cruza / 2) * 2
            # Y los n individuos a mutar solo el total deseado menos los que se ocuparán en cruza
            n_rutasMutar = n_NuevasRutas - n_rutasCruzar
            nuevaPoblacion = [] # Se inicializa la nueva población como lista vacía

            # Mutación:
            for index in range(n_rutasMutar):
                ind_RutaMutar = random.randrange(0, len(poblacion))
                # Se eligen dos puntos para intercambiar
                if (respetarPrimero): # Si respeta punto de partida la posición 0 no es opción
                    punto1 = random.randrange(1, len(poblacion[ind_RutaMutar]))
                    punto2 = random.randrange(1, len(poblacion[ind_RutaMutar]))
                else: # De lo contrario la posición 0 puede ser seleccionada
                    punto1 = random.randrange(0, len(poblacion[ind_RutaMutar]))
                    punto2 = random.randrange(0, len(poblacion[ind_RutaMutar]))
                nuevaRuta = poblacion[ind_RutaMutar].copy()
                # Se intercambian los puntos:
                nuevaRuta[punto1], nuevaRuta[punto2] = nuevaRuta[punto2], nuevaRuta[punto1]
                # Todo se va guardando en nuevaPoblación, aunque no sea la nueva población definitiva
                nuevaPoblacion.append(nuevaRuta)

            # Cruza:
            # Como ocupamos ruleta primero hay que construirla:
            ruleta = construirRuleta(fitness)
            for index in range(int(n_rutasCruzar / 2)):
                # Con ruleta obtenemos dos posiciones para la cruza
                ind_Ruta1Cruza = girarRuleta(ruleta)
                ind_Ruta2Cruza = girarRuleta(ruleta)
                # Se elige de manera aleatoria el punto de cruza
                puntoCruza = random.randrange(0, len(poblacion[0]))
                # PRIMER RESULTADO DE CRUZA ---------------------------------------------------------------------------
                puntosACruzar = []
                i = 0
                while (i <= puntoCruza):
                    punto = [] # Guarda el número a cruzar de una ruta y su posición en la otra ruta
                    punto.append(poblacion[ind_Ruta1Cruza][i])
                    punto.append(poblacion[ind_Ruta2Cruza].index(punto[0]))
                    puntosACruzar.append(punto)
                    i += 1
                # Ordena los puntos según su posición en la otra ruta
                puntosACruzar.sort(key=lambda punto: punto[1])
                # Para guardar el resultado de la cruza se crea la lista nuevaRuta
                nuevaRuta = []
                j = 0
                while (j < len(poblacion[0])):
                    if (j <= puntoCruza):
                        # Hasta el punto de cruza se guardan los números ya en el orden de la otra ruta
                        nuevaRuta.append(puntosACruzar[j][0])
                    else:
                        # En adelate se guardan los números tal cual estaban
                        nuevaRuta.append(poblacion[ind_Ruta1Cruza][j])
                    j += 1
                nuevaPoblacion.append(nuevaRuta)

                # SEGUNDO RESULTADO DE CRUZA -------------------------------------------------------------------------
                puntosACruzar = []
                # No se inicializa i porque guardo el valor anterior en que se quedó, el punto de cruza
                while (i < len(poblacion[0])):  # Hasta que termine la ruta
                    punto = [] # Guarda el número a cruzar de una ruta y su posición en la otra ruta
                    punto.append(poblacion[ind_Ruta2Cruza][i])
                    punto.append(poblacion[ind_Ruta1Cruza].index(punto[0]))
                    puntosACruzar.append(punto)
                    i += 1
                # Ordena los puntos según su posición en la otra ruta
                puntosACruzar.sort(key=lambda punto: punto[1])
                # Para guardar el resultado de la cruza se crea la lista nuevaRuta
                nuevaRuta = []
                j = 0
                j_puntos = 0
                while (j < len(poblacion[0])):
                    if (j <= puntoCruza):
                        # Hasta el punto de cruza se guardan los números tal cual estaban
                        nuevaRuta.append(poblacion[ind_Ruta2Cruza][j])
                    else:
                        # En adelante se guardan ya en el orden de la otra ruta
                        nuevaRuta.append(puntosACruzar[j_puntos][0])
                        j_puntos += 1
                    j += 1
                nuevaPoblacion.append(nuevaRuta)
            return nuevaPoblacion

        def crearPoblacionInicial(listaCoordenadas, tamPoblacion, respetarPrimero): # Devuelve población
            poblacion = [] # Inicializa la población como una lista
            # Primero nicializa una ruta con tamaño suficiente para cada coordenada en orden (0, 1, 2, ..., n)
            ruta = list(range(0, len(listaCoordenadas)))
            nuevaruta = ruta.copy()
            poblacion.append(nuevaruta) # Se agrega esta ruta a la población
            for i in range(tamPoblacion - 1):
                # Se van generando nuevas rutas mezclando sus valores de forma aleatoria
                nuevaruta = mezclarLista(ruta, respetarPrimero).copy()
                poblacion.append(nuevaruta)
            return poblacion

        def calcularFitness(poblacion, listaCoordenadas):  # Obtención del costo por camino, devuelve fitness
            fitness = [] # Inicializa fitness como una lista vacía
            # Se va a calcular el fitness de cada ruta
            for ruta in poblacion:
                nuevoFitness = 0.0
                punto = 0
                while punto < len(ruta) - 1: # '-1' porque no considera la última distancia (del último al primer punto)
                    coordenada1 = listaCoordenadas[ruta[punto]]
                    coordenada2 = listaCoordenadas[ruta[punto + 1]]
                    # La función fitness es la distancia entre dos puntos
                    distancia = math.sqrt(
                        (coordenada1[0] - coordenada2[0]) ** 2 + (coordenada1[1] - coordenada2[1]) ** 2)
                    nuevoFitness += distancia
                    punto += 1
                # Falta sumar la distancia del último punto al inicio, así que:
                coordenada1 = listaCoordenadas[ruta[punto]]  # Último punto
                coordenada2 = listaCoordenadas[ruta[0]]  # Inicio
                distancia = math.sqrt((coordenada1[0] - coordenada2[0]) ** 2 + (coordenada1[1] - coordenada2[1]) ** 2)
                nuevoFitness += distancia
                fitness.append(nuevoFitness)
            return fitness

        def construirRuleta(fitness): # Devuelve la ruleta
            valoresParaRuleta = []
            for valor in fitness:
                # Como el mejor es el mínimo, los valores se toman como:
                # Sumatoria de valores fitness / valor utilizado
                # Así mientras mas pequeño el npumero mayor oportunidad tendrá
                valoresParaRuleta.append(sum(fitness) / valor)
            # Esta ruleta va guardando el número correspondiente más el anterior
            ruleta = [0] * (len(valoresParaRuleta) + 1)
            index = 1
            for valor in valoresParaRuleta:
                ruleta[index] = valor + ruleta[index - 1]
                index += 1
            return ruleta

        def girarRuleta(ruleta): # Devuelve la posición elegida
            # Para "girarla" se seleccióna un número aleatorio entre 0 y el máximo(que es la sumatoria de todos)
            # Y como la ruleta está compuesta de los "límites" en cada posición
            # la posición elegida será la última en la que entre el número aleatorio.
            elegido = random.uniform(0, max(ruleta))
            for limite in ruleta:
                position = ruleta.index(limite)
                if (elegido < limite):
                    break
            position -= 1
            return position

        def seleccion(poblacion, nuevaPoblacion, fitness, nuevoFitness, respetarPrimero): # Devuelve los seleccionados
            # De la población actual y la nueva generada se eligen algunos para la nueva población OFICIAL
            individuosSeleccionados = []
            # Se combinan ambas poblaciones y sus fitness para encontrar las mejores
            fitnessCombinados = []
            fitnessCombinados.extend(fitness)
            fitnessCombinados.extend(nuevoFitness)
            poblacionCombinada = []
            poblacionCombinada.extend(poblacion)
            poblacionCombinada.extend(nuevaPoblacion)

            # Antes es importante que si el punto de partida es fijo se ingrese en primera posición la misma que era antes
            if(respetarPrimero):
                individuosSeleccionados.append(poblacionCombinada[0])
                fitnessCombinados.pop(0)
                poblacionCombinada.pop(0)
                rangoGenerar = len(poblacion)-1
            else:
                rangoGenerar = len(poblacion)

            for index in range(rangoGenerar):
                # Se busca el mejor individuo y un individuo aleatorio
                minPosicion = fitnessCombinados.index(min(fitnessCombinados))
                otraPosicion = random.randrange(0, len(fitnessCombinados))
                decision = random.uniform(0,1)
                # El mejor individuo hallado tiene 60% de probabilidad de pasar a la nueva población
                if(decision<=0.60):
                    individuosSeleccionados.append(poblacionCombinada[minPosicion])
                    fitnessCombinados.pop(minPosicion)
                    poblacionCombinada.pop(minPosicion)
                else:
                    individuosSeleccionados.append(poblacionCombinada[otraPosicion])
                    fitnessCombinados.pop(otraPosicion)
                    poblacionCombinada.pop(otraPosicion)
            return individuosSeleccionados

        def buscarMinimo(listaCoordenadas, respetarPrimero):# Devuelve la mejor ruta encontrada y su costo (distancia)
            global poblacion, fitness, iteracion, nuevaPoblacion, fitnessNuevaPob
            global mutacion  # Para que pueda irse mostrando su valor en la función "dibujarRuta()"
            iteracion = 0
            casosSinMejora = 0
            ronda1sinMejora = False
            ronda2sinMejora = False
            seguirBuscando = True
            mutacion = 0.3
            mutacionOriginal = 0.3
            poblacion = crearPoblacionInicial(listaCoordenadas, 60, respetarPrimero).copy()
            fitness = calcularFitness(poblacion, listaCoordenadas).copy()

            # Para ir dibujando las mejores rutas halladas:
            llevaSinDibujar = 0
            momentoDeDibujar = 40
            vecesDibujado = 0
            while (seguirBuscando):
                iteracion += 1
                def mandarADibujar (llevaSinDibujar, momentoDeDibujar, vecesDibujado): # Devuelve lo que recibe actualizado
                    global fitness, poblacion
                    # Se va a dibujar cada "momentoDeDibujar" itaraciones para ver las rutas que va encontrando
                    if (llevaSinDibujar == momentoDeDibujar):
                        vecesDibujado += 1
                        llevaSinDibujar = 0
                        # Cuando es momento de dibujar se manda a dibujar la mejor ruta de esta iteración
                        min_ind = fitness.index(min(fitness))
                        dibujarRuta(poblacion[min_ind], fitness[min_ind])
                    else:
                        llevaSinDibujar += 1
                    # Cuando ya se ha dibujado 10 veces es momento de empezar a dibujarlo con menos frecuencia (ya casi no cambia)
                    if(vecesDibujado == 10):
                        momentoDeDibujar = 100
                    return llevaSinDibujar, momentoDeDibujar, vecesDibujado
                llevaSinDibujar, momentoDeDibujar, vecesDibujado = mandarADibujar(llevaSinDibujar, momentoDeDibujar, vecesDibujado)

                # Siguiendo el algoritmo:
                # Se crea nueva población y calcula su fitness, se selecciona nueva población oficial y calcula su fitness
                nuevaPoblacion = crearNuevaPoblacion(poblacion, mutacion, 45, respetarPrimero, fitness).copy()
                fitnessNuevaPob = calcularFitness(nuevaPoblacion, listaCoordenadas).copy()
                poblacion = seleccion(poblacion, nuevaPoblacion, fitness, fitnessNuevaPob, respetarPrimero).copy()
                fitness = []
                fitness = calcularFitness(poblacion, listaCoordenadas).copy()

                # Para detener la busqueda:
                # Si no hay mejoría en 200 iteraciones, el valor original de mutación se multiplica * 2
                # Si despupués de eso no hay mejoría en 300 iteraciones, el valor original de mutación se divide / 2
                # Si despupués de eso no hay mejoría en 300 iteraciones, se detiene el algoritmo
                # Si en cualquier momento hay mejoría esta cuenta se reinicia y el valor de mutación vuelve al original
                if (iteracion == 1):
                    min_previo = min(fitness)
                min_ind = fitness.index(min(fitness))
                min_actual = fitness[min_ind]

                if (min_actual >= min_previo):
                    casosSinMejora += 1
                else:
                    min_previo = min_actual
                    casosSinMejora = 0
                    ronda1sinMejora = False
                    ronda2sinMejora = False
                    mutacion = mutacionOriginal

                if (casosSinMejora == 200 and not ronda1sinMejora and not ronda2sinMejora):
                    mutacion = mutacionOriginal * 2
                    ronda1sinMejora = True
                    casosSinMejora = 0
                elif (casosSinMejora == 300 and ronda1sinMejora and not ronda2sinMejora):
                    mutacion = mutacionOriginal / 2
                    ronda2sinMejora = True
                    casosSinMejora = 0
                elif (casosSinMejora == 300 and ronda2sinMejora):
                    seguirBuscando = False
            # Obtiene el índice del mejor individuo para devolver la mejor ruta y su costo
            min_ind = fitness.index(min(fitness))
            return (poblacion[min_ind], fitness[min_ind], iteracion)

        ruta, costo, iteraciones = buscarMinimo(coordenadas, respetarPrimero) # Se activa la búsqueda
        dibujarRuta(ruta, costo) # Se dibuja la mejor ruta final
        lb_iteraciones.configure(text='Se hicieron '+str(iteraciones)+' iteraciones')
        b_buscar.configure(text='Volver a buscar') # Da la oportunidad de volver a buscar (la ruta podría cambiar)
        b_buscar.configure(state=tkinter.NORMAL)

    def irMenuPrincipal():
        plt.close(fig)
        ven_Busqueda.destroy()
        crearMenuPrincipal()

    def nuevoMapa(guardarPartida):
        plt.close(fig)
        solicitarDimensiones(ven_Busqueda, guardarPartida)

    # Generación de nueva ventana / formato al plot / inclusión plot-tkinter
    ven_Anterior.destroy()
    ven_Busqueda = tkinter.Tk()
    ven_Busqueda.title('Buscador de ruta')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, ven_Busqueda)  # Se agrega el "plot" a la ventana tkinter
    canvas.draw()  # Para mostrar el plot
    esPrimeraCoordenada = True
    for punto in coordenadas:
        if (esPrimeraCoordenada and respetarPrimero):
            plt.plot(punto[0], punto[1], 'rX')
            esPrimeraCoordenada = False
        else:
            plt.plot(punto[0], punto[1], 'o')
    fig.canvas.draw()
    formatoDePlot()
    plt.grid()
    fig.canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1, pady=10, padx=10)

    # Adición de etiquetas y botones a la ventana:
    rightFrame = tkinter.Frame(ven_Busqueda)
    tkinter.Label(rightFrame, text='\n', font='Helvetica 5').pack()
    lb_numBusqueda = tkinter.Label(rightFrame, text='BÚSQUEDA', font='Helvetica 20 bold')
    lb_numBusqueda.pack()
    tkinter.Label(rightFrame, text='Se está trabajando con:', font='Helvetica 12').pack()
    lb_cruzaMut = tkinter.Label(rightFrame, text=' - Rango de cruza = 0.7\n - Rango de mutación = 0.3',
                                font = 'Helvetica 12')
    lb_cruzaMut.pack()
    tkinter.Label(rightFrame, text=' - Tamaño de población = 60', font='Helvetica 12').pack()
    lb_puntoPartida = tkinter.Label(rightFrame, text=('(    ,    )'),
                                    font='Helvetica 12 bold')
    lb_puntoPartida.pack()
    tkinter.Label(rightFrame, text='Distancia de esta ruta:', font='Helvetica 12').pack()
    lb_costoMin = tkinter.Label(rightFrame, text='-', font='Helvetica 12 bold')
    lb_costoMin.pack()
    lb_iteraciones = tkinter.Label(rightFrame, text=' ', font='Helvetica 13')
    lb_iteraciones.pack()
    b_buscar = tkinter.Button(rightFrame, text='Encontrar ruta', font='Helvetica 12', height=2, width=17,
                              command=iniciarBusqueda)
    b_buscar.configure(relief='groove', bg="gold", activebackground='gold3', activeforeground='black')
    b_buscar.pack(padx=10, pady=2)
    b_nuevoMap_Partida = tkinter.Button(rightFrame, text='NUEVO MAPA\ncon punto de partida', font='Helvetica 12',
                                        height=2, width=17,
                                        command=lambda: nuevoMapa(True))
    b_nuevoMap_Partida.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                                 activeforeground='black')
    b_nuevoMap_Partida.pack(padx=10, pady=2)
    b_nuevoMap_NoPartida = tkinter.Button(rightFrame, text='NUEVO MAPA\nsin punto de partida', font='Helvetica 12',
                                          height=2, width=17,
                                          command=lambda: nuevoMapa(False))
    b_nuevoMap_NoPartida.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                                   activeforeground='black')
    b_nuevoMap_NoPartida.pack(padx=10, pady=2)
    b_MenuPrincipal = tkinter.Button(rightFrame, text='Menú Principal', font='Helvetica 12', height=2, width=17,
                                     command=irMenuPrincipal)
    b_MenuPrincipal.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                              activeforeground='black')
    b_MenuPrincipal.pack(padx=10, pady=2)
    tkinter.Label(rightFrame, text='\n', font='Helvetica 5').pack()
    rightFrame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, pady=10, padx=10)

    def on_closing():
        plt.close(fig)
        try:
            ven_Busqueda.destroy()
        except:
            ven_Busqueda.destroy()

    ven_Busqueda.protocol("WM_DELETE_WINDOW", on_closing)

    ven_Busqueda.mainloop()

def crearMapa(ven_Anterior, xInf, xSup, yInf, ySup, respetarPrimero):
    global lb_TotalPuntos, lb_PuntoPartida, val_totalPuntos, esPrimeraCoordenada
    esPrimeraCoordenada = True
    val_totalPuntos = 0

    # Funciones utilizadas en esta ventana
    def onclick(event): # Event guarda información sobre la posición  del clic en el mapa
        # Esta función es para deinir lo que ocurre cuando se cliquea el mapa de pyplot:
        global coordenadas, esPrimeraCoordenada
        global val_totalPuntos, lb_TotalPuntos, lb_PuntoPartida
        try: # Se utiliza try porque marca error si el usuario cliquea fuera de el gráfico
            if(esPrimeraCoordenada and respetarPrimero):
                plt.plot(event.xdata, event.ydata, "rX")
                esPrimeraCoordenada = False
            else:
                plt.plot(event.xdata, event.ydata, "o") # Se agrega un punto en el sitio que se cliqueó
            fig.canvas.draw() # Se dibuja el cambio para hacer visible el punto cliqueado
            nuevoPunto = [] # Aquí se van a guardar las coordenadas del punto seleccionado
            nuevoPunto.append(round(event.xdata, 2))
            nuevoPunto.append(round(event.ydata, 2))
            coordenadas.append(nuevoPunto) # Y ese punto se guarda en "coordenadas"
        except ValueError:
            msb.showerror(title='Error', message='La selección debe estar dentro del mapa')
        else:  # Si no hubo ValueError
            val_totalPuntos += 1 # Se aumenta el contador de puntos en coordenadas
            lb_TotalPuntos.configure(text=str(val_totalPuntos))  # Se modifica la etiqueta que muestra el total de puntos
            if (val_totalPuntos == 1 and respetarPrimero): # Si se está trabajando con punto de partida:
                partida = '(' + str(round(event.xdata, 2)) + ' , ' + str(round(event.ydata, 2)) + ')'
                lb_PuntoPartida.configure(text=partida) # Se muestra el punto de partida

    def formatoDePlot():
        # Le da formato al título del plot
        ax.set_title("MAPA", fontsize='large', color='black', weight='bold')
        # Le da formato a las etiquetas de los ejes del plot
        for tick in ax.xaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')
        for tick in ax.yaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')

    def limpiar(): # Si se desean quitar los puntos registrados y volver a iniciar
        # Se necesitan los siguientes datos globales para reiniciarlos
        global numbPlace, lb_TotalPuntos, val_totalPuntos, lb_PuntoPartida, coordenadas, esPrimeraCoordenada
        esPrimeraCoordenada = True
        coordenadas = []
        lb_TotalPuntos.configure(text='0')
        if (respetarPrimero):
            lb_PuntoPartida.configure(text='(    ,    )')
        val_totalPuntos = 0
        numbPlace = 0
        # Una vez reiniciados los valores se limpia el gráfico y se le vuelve a dar formato
        ax.clear()
        ax.set_xlim([xInf, xSup])
        ax.set_ylim([yInf, ySup])
        formatoDePlot()
        plt.grid()
        fig.canvas.draw()

    def guardar(): # Permite guardar el mapa como un archivo '.txt'
        global coordenadas, val_totalPuntos
        # Primero debe validarse que el camino cuente con al menos dos puntos para desplazarse
        if (val_totalPuntos >= 2):
            file = asksaveasfile(mode='w', defaultextension=".txt")  # Para trabajar desde el explorador
            if (file is not None): # Para evitar error si el usuario cancela la operación y no adjunta archivo
                # Se guarda una coordenada por línea... x & y separados por un espacio
                for par in coordenadas:
                    for dato in par:
                        file.write(str(dato) + ' ')  # Guarda x & y separados por espacios
                    file.write('\n')  # Cambia de linea para ir a la siguiente coordenada (si hay)
                file.close()  # Deja de escribir en el archivo
        else:
            msb.showerror(title='Error', message='Asegúrate de que la ruta cuente con al menos dos posiciones')

    def menuPrincipal(): # Destruye ventana actual y lleva al menú de inicio
        plt.close(fig)
        ven_Creacion.destroy()
        crearMenuPrincipal()

    def continuar(): # Avanza a la ventana de ejecución del algoritmo de aprendizaje
        global val_totalPuntos
        # No permite avanzar si hay menos de dos puntos para desplazarse
        if (val_totalPuntos >= 2):
            plt.close(fig)
            buscarCostoMinimo(ven_Creacion, respetarPrimero)
        else:
            msb.showerror(title='Error', message='Asegúrate de que la ruta cuente con al menos dos posiciones')

    # Generación de nueva ventana / formato al plot / inclusión plot-tkinter
    ven_Anterior.destroy()
    ven_Creacion = tkinter.Tk()
    ven_Creacion.title('Creación de mapa')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim([xInf, xSup])
    ax.set_ylim([yInf, ySup])
    canvas = FigureCanvasTkAgg(fig, ven_Creacion)
    canvas.draw()
    fig.canvas.mpl_connect('button_press_event', onclick) # Para que sea sensible al clic del usuario
    formatoDePlot()
    plt.grid()
    fig.canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1, pady=10, padx=10)

    # Adición de botones y etiquetas
    botonesFrame = tkinter.Frame(ven_Creacion)
    tkinter.Label(botonesFrame, text='\n', font='Helvetica 10').pack()
    if (respetarPrimero):
        tkinter.Label(botonesFrame, text='Debes seleccionar el\npunto de partida antes\nde las demás coordenadas',
                      font='Helvetica 12').pack()
    else:
        tkinter.Label(botonesFrame, text='Debes seleccionar el\nlos puntos a considerar\nen la ruta a analizar',
                      font='Helvetica 12').pack()
    tkinter.Label(botonesFrame, text='Lugares en ruta: ', font='Helvetica 12').pack()
    lb_TotalPuntos = tkinter.Label(botonesFrame, text='0', font='Helvetica 12')
    lb_TotalPuntos.pack()
    if(respetarPrimero):
        tkinter.Label(botonesFrame, text='Punto de partida: ', font='Helvetica 12').pack()
        lb_PuntoPartida = tkinter.Label(botonesFrame, text='(    ,    )', font='Helvetica 12')
        lb_PuntoPartida.pack()
    tkinter.Label(botonesFrame, text='\n', font='Helvetica 10').pack()
    b_Limpiar = tkinter.Button(botonesFrame, text="LIMPIAR", font='Helvetica 12', height=2, width=17, command=limpiar)
    b_Limpiar.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3', activeforeground='black')
    b_Limpiar.pack(padx=10, pady=2)
    b_Guardar = tkinter.Button(botonesFrame, text="GUARDAR", font='Helvetica 12', height=2, width=17, command=guardar)
    b_Guardar.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3', activeforeground='black')
    b_Guardar.pack(padx=10, pady=2)
    b_Menu = tkinter.Button(botonesFrame, text="MENU PRINCIPAL", font='Helvetica 12', height=2, width=17,
                            command=menuPrincipal)
    b_Menu.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3', activeforeground='black')
    b_Menu.pack(padx=10, pady=2)
    b_Continuar = tkinter.Button(botonesFrame, text="CONTINUAR", font='Helvetica 12', height=2, width=17,
                                 command=continuar)
    b_Continuar.configure(relief='groove', bg="gold", activebackground='gold3', activeforeground='black')
    b_Continuar.pack(padx=10, pady=2)
    botonesFrame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, pady=10, padx=10)

    def on_closing():
        plt.close(fig)
        try:
            ven_Creacion.destroy()
        except:
            ven_Creacion.destroy()

    ven_Creacion.protocol("WM_DELETE_WINDOW", on_closing)

    ven_Creacion.mainloop()

def solicitarDimensiones(ven_Anterior, respetarPrimero):
    # Esta ventana solicita las dimensiones con que se creará el nuevo mapa
    global coordenadas
    coordenadas = [] # Se limpia coordenadas porque comenzará una nueva selección de puntos

    # Funciones utilizadas en esta ventana
    def continuar(): # Dirige a la ventana de creación del mapa
        global continuaBandera # Se utiliza para corroborar que haya ingresado límites válidos para los ejes
        # Se obtiene la información registrada por el usuario
        xInf = int(xInfBox.get())
        xSup = int(xSupBox.get())
        yInf = int(yInfBox.get())
        ySup = int(ySupBox.get())
        continuaBandera = False # Comienza sin permiso para continuar
        try: # Con una operación simple verificamos que ingresó datos numéricos si no marca error
            xInf + xSup + yInf + ySup
        except ValueError:
            msb.showerror(title='Error', message='Valor incompatible, para continuar intente de nuevo')
        else:
            # Ya comprobado el formato numérico, se verifica que haya coherencia entre los valores
            if (xInf >= xSup or yInf >= ySup):
                msb.showerror(title='Error', message='Límites inválidos, para continuar intente de nuevo')
            else:
                continuaBandera = True

        if (continuaBandera): # Si pasó los dos filtros de validación puede continuar
            crearMapa(ven_Dimensiones, xInf, xSup, yInf, ySup, respetarPrimero)

    def menuPrincipal(): # Destruye la ventana actual y lleva al menú de inicio
        ven_Dimensiones.destroy()
        crearMenuPrincipal()

    # Generación de nueva ventana
    ven_Anterior.destroy()
    ven_Dimensiones = tkinter.Tk()
    ven_Dimensiones.title('Dimensiones')
    ven_Dimensiones.geometry('370x210')
    ven_Dimensiones.configure(bg='mintcream')

    # Adición de etiquetas, cuadros de texto y botones
    tkinter.Label(ven_Dimensiones, text='CONFIGURACIÓN DE DIMESNIONES', font='Helvetica 14 bold', bg='mintcream').place(
        x=15, y=10)
    tkinter.Label(ven_Dimensiones, text='HORIZONTAL', font='Helvetica 12 bold', bg='mintcream').place(x=50, y=40)
    tkinter.Label(ven_Dimensiones, text='VERTICAL', font='Helvetica 12 bold', bg='mintcream').place(x=225, y=40)
    tkinter.Label(ven_Dimensiones, text='Límite inferior:', font='Helvetica 12', bg='mintcream').place(x=10, y=75)
    tkinter.Label(ven_Dimensiones, text='Límite superior:', font='Helvetica 12', bg='mintcream').place(x=10, y=105)
    tkinter.Label(ven_Dimensiones, text='Límite inferior:', font='Helvetica 12', bg='mintcream').place(x=190, y=75)
    tkinter.Label(ven_Dimensiones, text='Límite superior:', font='Helvetica 12', bg='mintcream').place(x=190, y=105)

    # Los cuadros de texto soportarpan valores entre -5000 y 5000
    xInfBox = tkinter.Spinbox(ven_Dimensiones, font='Helvetica 12', width='5', justify='center', relief='flat',
                              buttondownrelief='flat', buttonuprelief='flat', buttonbackground='lightskyblue1',
                              from_=-5000, to=5000)
    xInfBox.place(x=125, y=75)
    xInfBox.delete(0, 'end')
    xInfBox.insert(0, 0)

    xSupBox = tkinter.Spinbox(ven_Dimensiones, font='Helvetica 12', width='5', justify='center', relief='flat',
                              buttondownrelief='flat', buttonuprelief='flat', buttonbackground='lightskyblue1',
                              from_=-5000, to=5000)
    xSupBox.place(x=125, y=105)
    xSupBox.delete(0, 'end')
    xSupBox.insert(0, 0)

    yInfBox = tkinter.Spinbox(ven_Dimensiones, font='Helvetica 12', width='5', justify='center', relief='flat',
                              buttondownrelief='flat', buttonuprelief='flat', buttonbackground='lightskyblue1',
                              from_=-5000, to=5000)
    yInfBox.place(x=305, y=75)
    yInfBox.delete(0, 'end')
    yInfBox.insert(0, 0)

    ySupBox = tkinter.Spinbox(ven_Dimensiones, font='Helvetica 12', width='5', justify='center', relief='flat',
                              buttondownrelief='flat', buttonuprelief='flat', buttonbackground='lightskyblue1',
                              from_=-5000, to=5000)
    ySupBox.place(x=305, y=105)
    ySupBox.delete(0, 'end')
    ySupBox.insert(0, 0)

    b_continuar = tkinter.Button(ven_Dimensiones, text='CONTINUAR', font='Helvetica 12', height=2, width=15)
    b_continuar.configure(relief='groove', bg="greenyellow", activebackground='yellowgreen', activeforeground='black',
                          command=continuar)
    b_continuar.place(x=200, y=145)
    b_menuPrincipal = tkinter.Button(ven_Dimensiones, text='MENU PRINCIPAL', font='Helvetica 12', height=2, width=15)
    b_menuPrincipal.configure(relief='groove', bg="greenyellow", activebackground='yellowgreen',
                              activeforeground='black',
                              command=menuPrincipal)
    b_menuPrincipal.place(x=25, y=145)

    # Mantiene la ventana ativa
    ven_Dimensiones.mainloop()

def crearMenuPrincipal():
    global coordenadas
    coordenadas = []
    # Se crea la ventana principal y se configuran sus características
    ven_Principal = tkinter.Tk()
    ven_Principal.title('Menú Principal')
    ven_Principal.geometry('455x245')
    ven_Principal.configure(bg='mintcream')
    # Se agregan las etiquetas y botones que se mostrarán en la ventana Principal
    tkinter.Label(ven_Principal, text='PROBLEMA DEL VIAJERO', font='Helvetica 25 bold',
                  foreground='black', bg='mintcream').place(x=15, y=8)
    # El botón crear mapa debe llevar a la ventana Dimensiones
    # Hay dos botones porque uno indica que se dará el punto de partida y el otro que no
    crearMapa = tkinter.Button(ven_Principal, text='CREAR MAPA\ncon punto de partida', height=3, width=17)
    crearMapa.configure(relief='groove', font='Helvetica 14 bold', bg="lightskyblue",
                        fg='black', activebackground='lightskyblue3', activeforeground='black',
                        command=lambda ventana=ven_Principal: solicitarDimensiones(ventana, True))
    crearMapa.place(x=10, y=55)

    crearMapa2 = tkinter.Button(ven_Principal, text='CREAR MAPA\nsin punto de partida', height=3, width=17)
    crearMapa2.configure(relief='groove', font='Helvetica 14 bold', bg="greenyellow",
                         fg='black', activebackground='yellowgreen', activeforeground='black',
                         command=lambda ventana=ven_Principal: solicitarDimensiones(ventana, False))
    crearMapa2.place(x=235, y=55)
    # El botón cargar mapa debe abrir el explorador de archivos.. usa "askopenfile"
    cargarMapa_cInicio = tkinter.Button(ven_Principal, text='CARGAR MAPA\ncon punto de partida', height=3, width=17)
    cargarMapa_cInicio.configure(relief='groove', font='Helvetica 14 bold', bg="gold",
                         fg='black', activebackground='gold3', activeforeground='black',
                         command=lambda ventana=ven_Principal: cargarArchivo(ventana, True))
    cargarMapa_cInicio.place(x=10, y=147)
    # Botón para salir del programa destruye la ventana
    cargarMapa_sInicio = tkinter.Button(ven_Principal, text='CARGAR MAPA\nsin punto de partida', height=3, width=17)
    cargarMapa_sInicio.configure(relief='groove', font='Helvetica 14 bold', bg="brown1",
                    fg='black', activebackground='firebrick1', activeforeground='black',
                    command=lambda ventana=ven_Principal: cargarArchivo(ventana, False))
    cargarMapa_sInicio.place(x=235, y=147)

    # Se mantiene activa la ventana Principal
    ven_Principal.mainloop()

# Se llama la función que crea el menú principal para iniciar el programa
crearMenuPrincipal()