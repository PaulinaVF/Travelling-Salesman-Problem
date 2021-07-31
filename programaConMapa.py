# Combinación, ocupa ruleta, no es totalmente elitista
# Ya no fija el usuario las dimensiones, se hace sobre un mapamundi a escala
# Se eliminó la opción de limpiar mapa mientras se están eligiendo los puntos

import matplotlib.pyplot as plt
import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from tkinter import messagebox as msb
from tkinter.filedialog import asksaveasfile
import math
import random

global coordenadas  # Guarda los puntos a considerar en la ruta.. En la posición 0 va el punto de partida

def cargarArchivo(ven_Anterior, respetarPrimero):  # Se lee el archivo y se generan dos listas; 1 de coordenadas X, y una de coordenadas Y
    global coordenadas
    coordenadas = []
    archivo = tkinter.filedialog.askopenfile(title="Select file",
                                             filetypes=(("text files", "*.txt"), ("all files", "*.*")))
    if archivo is not None:
        mapaCoordenadas = archivo.readlines()
        for coordenada in mapaCoordenadas:
            splitCoord = coordenada.split(" ")
            splitCoord.pop()
            coordenadas.append(list(map(float, splitCoord)))
        buscarCostoMinimo(ven_Anterior, respetarPrimero)

def buscarCostoMinimo(ven_Anterior, respetarPrimero):
    global coordenadas, lb_costoMin, lb_puntoPartida, b_buscar
    ven_Anterior.destroy()
    ven_Busqueda = tkinter.Tk()
    ven_Busqueda.title('Buscador de ruta')
    fig = plt.figure(figsize=(834 / 90, 574 / 90), dpi=90)
    ax = fig.add_subplot(111)

    img = plt.imread("mapa.png")
    ax.imshow(img)

    canvas = FigureCanvasTkAgg(fig, ven_Busqueda)
    canvas.draw()

    def dibujarRuta(ruta, costo):
        ax.clear()
        img = plt.imread("mapa.png")
        plt.imshow(img)
        formatoDePlot()
        esPrimeraCoordenada = True
        for punto in ruta:
            if (esPrimeraCoordenada):
                plt.plot(coordenadas[punto][0], coordenadas[punto][1], 'rX')
                esPrimeraCoordenada = False
            else:
                plt.plot(coordenadas[punto][0], coordenadas[punto][1], 'o')
        fig.canvas.draw()
        coordX_proporcion = round(coordenadas[ruta[0]][0]*40000/834,2)
        coordY_proporcion = 40000 - round(coordenadas[ruta[0]][1]*40000/574,2)
        lb_puntoPartida.configure(text=('(' + str(coordX_proporcion) + ' , ' + str(round(coordY_proporcion)) + ')'))
        round(costo, 2)
        lb_costoMin.configure(text=str(costo)+' km')
        i = 0
        while (i < len(ruta) - 1):
            x_values = [coordenadas[ruta[i]][0], coordenadas[ruta[i + 1]][0]]
            y_values = [coordenadas[ruta[i]][1], coordenadas[ruta[i + 1]][1]]
            plt.plot(x_values, y_values, color='black')
            i += 1
        x_values = [coordenadas[ruta[i]][0], coordenadas[ruta[0]][0]]
        y_values = [coordenadas[ruta[i]][1], coordenadas[ruta[0]][1]]
        plt.plot(x_values, y_values, color='black')
        fig.canvas.draw()

    def formatoDePlot():
        # Set the font size via a keyword argument
        ax.set_title("MAPA", fontsize='large', color='black', weight='bold')
        # Retrieve an element of a plot and set properties
        ax.set_xticks([208.5, 417, 625.5, 834])
        ax.set_xticklabels(['10000', '20000', '30000', '40000'])
        ax.set_yticks([430.5, 287, 143.5, 0])
        ax.set_yticklabels(['10000', '20000', '30000', '40000'])
        for tick in ax.xaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')
        for tick in ax.yaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')

    def iniciarBusqueda():
        b_buscar.configure(state=tkinter.DISABLED)

        def mezclarLista(listaParaMezclar, respetarPrimero):  # El argumento respetar primero si es True no cambia el valor del dato en posición 0 si es False, si lo mezvla
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

        def crearNuevaPoblacion(poblacion, mutacion, n_NuevasRutas, respetarPrimero, fitness):
            cruza = 1 - mutacion
            n_rutasCruzar = math.ceil(n_NuevasRutas * cruza / 2) * 2
            n_rutasMutar = n_NuevasRutas - n_rutasCruzar
            nuevaPoblacion = []

            # Mutación:
            for index in range(n_rutasMutar):
                ind_RutaMutar = random.randrange(0, len(poblacion))
                if (respetarPrimero):
                    punto1 = random.randrange(1, len(poblacion[ind_RutaMutar]))
                    punto2 = random.randrange(1, len(poblacion[ind_RutaMutar]))

                else:
                    punto1 = random.randrange(0, len(poblacion[ind_RutaMutar]))
                    punto2 = random.randrange(0, len(poblacion[ind_RutaMutar]))
                nuevaRuta = poblacion[ind_RutaMutar].copy()
                nuevaRuta[punto1], nuevaRuta[punto2] = nuevaRuta[punto2], nuevaRuta[punto1]
                nuevaPoblacion.append(nuevaRuta)

            # Cruza:
            ruleta = construirRuleta(fitness)
            for index in range(int(n_rutasCruzar / 2)):
                ind_Ruta1Cruza = girarRuleta(ruleta)
                ind_Ruta2Cruza = girarRuleta(ruleta)
                puntoCruza = random.randrange(0, len(poblacion[0]))
                # Cruza del primer elemento
                puntosACruzar = []
                i = 0
                while (i <= puntoCruza):
                    punto = []
                    punto.append(poblacion[ind_Ruta1Cruza][i])
                    punto.append(poblacion[ind_Ruta2Cruza].index(punto[0]))
                    puntosACruzar.append(punto)
                    i += 1
                puntosACruzar.sort(key=lambda punto: punto[1])
                nuevaRuta = []
                j = 0
                while (j < len(poblacion[0])):
                    if (j <= puntoCruza):
                        nuevaRuta.append(puntosACruzar[j][0])
                    else:
                        nuevaRuta.append(poblacion[ind_Ruta1Cruza][j])
                    j += 1
                nuevaPoblacion.append(nuevaRuta)

                # Cruza del segundo elemento
                puntosACruzar = []
                while (i < len(poblacion[0])):  # Mientras que sea menor al tamaño de un camino
                    punto = []
                    punto.append(poblacion[ind_Ruta2Cruza][i])
                    punto.append(poblacion[ind_Ruta1Cruza].index(punto[0]))
                    puntosACruzar.append(punto)
                    i += 1
                puntosACruzar.sort(key=lambda punto: punto[1])
                nuevaRuta = []
                j = 0
                j_puntos = 0
                while (j < len(poblacion[0])):
                    if (j <= puntoCruza):
                        nuevaRuta.append(poblacion[ind_Ruta2Cruza][j])
                    else:
                        nuevaRuta.append(puntosACruzar[j_puntos][0])
                        j_puntos += 1
                    j += 1
                nuevaPoblacion.append(nuevaRuta)
            return nuevaPoblacion

        def crearPoblacionInicial(listaCoordenadas, tamPoblacion, respetarPrimero):
            poblacion = []
            ruta = list(range(0, len(listaCoordenadas)))
            nuevaruta = ruta.copy()
            poblacion.append(nuevaruta)
            for i in range(tamPoblacion - 1):
                nuevaruta = mezclarLista(ruta, respetarPrimero).copy()
                poblacion.append(nuevaruta)
            return poblacion

        def calcularFitness(poblacion, listaCoordenadas):  # Obtención del costo por camino
            fitness = []
            for ruta in poblacion:
                nuevoFitness = 0.0
                punto = 0
                while punto < len(ruta) - 1:
                    coordenada1 = listaCoordenadas[ruta[punto]]
                    coordenada2 = listaCoordenadas[ruta[punto + 1]]
                    distancia = math.sqrt(
                        (coordenada1[0] - coordenada2[0]) ** 2 + (coordenada1[1] - coordenada2[1]) ** 2)
                    nuevoFitness += distancia
                    punto += 1
                # Falta sumar la distancia del último punto al inicio, así que:
                coordenada1 = listaCoordenadas[ruta[punto]]  # Último punto
                coordenada2 = listaCoordenadas[ruta[0]]  # Inicio
                distancia = math.sqrt((coordenada1[0] - coordenada2[0]) ** 2 + (coordenada1[1] - coordenada2[1]) ** 2)
                nuevoFitness += distancia
                fitness_proporcion = round(nuevoFitness * 40000 / 674, 2)
                fitness.append(fitness_proporcion)
            return fitness

        def construirRuleta(fitness):
            valoresParaRuleta = []
            for valor in fitness:
                valoresParaRuleta.append(sum(fitness) / valor)
            ruleta = [0] * (len(valoresParaRuleta) + 1)
            index = 1
            for valor in valoresParaRuleta:
                ruleta[index] = valor + ruleta[index - 1]
                index += 1
            return ruleta

        def girarRuleta(ruleta):
            elegido = random.uniform(0, max(ruleta))
            for limite in ruleta:
                position = ruleta.index(limite)
                if (elegido < limite):
                    break
            position -= 1
            return position

        def seleccion(poblacion, nuevaPoblacion, fitness, nuevoFitness, respetarPrimero):
            individuosSeleccionados = []
            fitnessCombinados = []
            fitnessCombinados.extend(fitness)
            fitnessCombinados.extend(nuevoFitness)
            poblacionCombinada = []
            poblacionCombinada.extend(poblacion)
            poblacionCombinada.extend(nuevaPoblacion)

            if(respetarPrimero):
                individuosSeleccionados.append(poblacionCombinada[0])
                fitnessCombinados.pop(0)
                poblacionCombinada.pop(0)
                rangoGenerar = len(poblacion)-1
            else:
                rangoGenerar = len(poblacion)

            for index in range(rangoGenerar):
                minPosicion = fitnessCombinados.index(min(fitnessCombinados))
                otraPosicion = random.randrange(0, len(fitnessCombinados))
                decision = random.uniform(0,1)
                if(decision<=0.60):
                    individuosSeleccionados.append(poblacionCombinada[minPosicion])
                    fitnessCombinados.pop(minPosicion)
                    poblacionCombinada.pop(minPosicion)
                else:
                    individuosSeleccionados.append(poblacionCombinada[otraPosicion])
                    fitnessCombinados.pop(otraPosicion)
                    poblacionCombinada.pop(otraPosicion)
            return individuosSeleccionados

        def buscarMinimo(listaCoordenadas, respetarPrimero):
            global poblacion, fitness, iteracion, nuevaPoblacion, fitnessNuevaPob
            # Para graficar la busqueda--------------------------------
            iteracion = 0
            casosSinMejora = 0
            ronda1sinMejora = False
            ronda2sinMejora = False
            seguirBuscando = True
            mutacion = 0.3
            mutacionOriginal = 0.3
            promFitness = []
            indIteracion = []
            # ---------------------------------------------------------

            poblacion = crearPoblacionInicial(listaCoordenadas, 60, respetarPrimero).copy()
            fitness = calcularFitness(poblacion, listaCoordenadas).copy()

            dibujarCadaN = 0
            n = 40
            vecesDibujado = 0
            while (seguirBuscando):
                if (dibujarCadaN == n):
                    vecesDibujado += 1
                    dibujarCadaN = 0
                    min_ind = fitness.index(min(fitness))
                    dibujarRuta(poblacion[min_ind], fitness[min_ind])
                dibujarCadaN += 1
                if(vecesDibujado == 8):
                    n = 100
                # Para graficar la busqueda---------------------------------
                iteracion += 1
                tempPromFit = sum(fitness) / len(poblacion)
                promFitness.append(tempPromFit)
                indIteracion.append(iteracion)
                # -----------------------------------------------------------
                # Para detener la búsqueda----------------------------------
                if (iteracion == 1):
                    min_previo = min(fitness)
                # ----------------------------------------------------------
                nuevaPoblacion = crearNuevaPoblacion(poblacion, mutacion, 45, respetarPrimero, fitness).copy()
                fitnessNuevaPob = calcularFitness(nuevaPoblacion, listaCoordenadas).copy()
                poblacion = seleccion(poblacion, nuevaPoblacion, fitness, fitnessNuevaPob, respetarPrimero).copy()
                fitness = []
                fitness = calcularFitness(poblacion, listaCoordenadas).copy()

                # Para detener la busqueda -----------------------------------------------------
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

            min_ind = fitness.index(min(fitness))
            return (poblacion[min_ind], fitness[min_ind])

        ruta, costo = buscarMinimo(coordenadas, respetarPrimero)
        dibujarRuta(ruta, costo)
        b_buscar.configure(text='Volver a buscar')
        b_buscar.configure(state=tkinter.NORMAL)

    esPrimeraCoordenada = True
    for coordenada in coordenadas:
        if(esPrimeraCoordenada and respetarPrimero):
            plt.plot(coordenada[0], coordenada[1], 'rX')
            esPrimeraCoordenada = False
        else:
            plt.plot(coordenada[0], coordenada[1], 'o')
    fig.canvas.draw()

    def irMenuPrincipal():
        ven_Busqueda.destroy()
        crearMenuPrincipal()

    def irNuevoMapa(respPrimero):
        global coordenadas
        coordenadas = []
        crearMapa(ven_Busqueda, respPrimero)

    rightFrame = tkinter.Frame(ven_Busqueda)
    tkinter.Label(rightFrame, text='\n', font='Helvetica 5').pack()
    lb_numBusqueda = tkinter.Label(rightFrame, text='BUSQUEDA', font='Helvetica 20 bold')
    lb_numBusqueda.pack()
    tkinter.Label(rightFrame, text='\nEn este mapa se considera\ncomo punto de partida \nel sitio con coordenadas',
                  font='Helvetica 12').pack()
    if(respetarPrimero):
        coordX_proporcion = round(coordenadas[0][0] * 40000 / 834, 2)
        coordY_proporcion = 40000 - round(coordenadas[0][1] * 40000 / 574, 2)
        lb_puntoPartida = tkinter.Label(rightFrame, text=('(' + str(coordX_proporcion) + ' , ' + str(round(coordY_proporcion)) + ')'),
                                        font='Helvetica 12 bold')
    else:
        lb_puntoPartida = tkinter.Label(rightFrame, text=('(    ,    )'), font='Helvetica 12 bold')
    lb_puntoPartida.pack()
    tkinter.Label(rightFrame, text='Se muestran los mejores\ncaminos encontrados hasta\nel momento',
                  font='Helvetica 12').pack()
    tkinter.Label(rightFrame, text='Menor distancia en esta búsqueda:', font='Helvetica 12').pack()
    lb_costoMin = tkinter.Label(rightFrame, text='-', font='Helvetica 12 bold')
    lb_costoMin.pack()
    tkinter.Label(rightFrame, text='\n', font='Helvetica 10').pack()

    b_buscar = tkinter.Button(rightFrame, text='Encontrar ruta', font='Helvetica 12', height=2, width=17,
                              command=iniciarBusqueda)
    b_buscar.configure(relief='groove', bg="gold", activebackground='gold3', activeforeground='black')
    b_buscar.pack(padx=10, pady=2)
    b_nuevoMap_Partida = tkinter.Button(rightFrame, text='NUEVO MAPA\ncon punto de partida', font='Helvetica 12',
                                        height=2, width=17,
                                        command=lambda: irNuevoMapa(True))
    b_nuevoMap_Partida.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                                 activeforeground='black')
    b_nuevoMap_Partida.pack(padx=10, pady=2)
    b_nuevoMap_NoPartida = tkinter.Button(rightFrame, text='NUEVO MAPA\nsin punto de partida', font='Helvetica 12',
                                          height=2, width=17,
                                          command=lambda: irNuevoMapa(False))
    b_nuevoMap_NoPartida.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                                   activeforeground='black')
    b_nuevoMap_NoPartida.pack(padx=10, pady=2)
    b_MenuPrincipal = tkinter.Button(rightFrame, text='Menú principal', font='Helvetica 12', height=2, width=17,
                                     command=irMenuPrincipal)
    b_MenuPrincipal.configure(relief='groove', bg="dodgerblue", activebackground='dodgerblue3',
                              activeforeground='black')
    b_MenuPrincipal.pack(padx=10, pady=2)
    rightFrame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, pady=10, padx=10)

    formatoDePlot()
    plt.grid()
    fig.canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1, pady=10, padx=10)
    ven_Busqueda.mainloop()

def crearMapa(ven_Anterior, respetarPrimero):
    global lb_TotalPuntos, lb_PuntoPartida, val_totalPuntos, coordenadas
    coordenadas = []
    val_totalPuntos = 0
    ven_Anterior.destroy()
    ven_Creacion = tkinter.Tk()
    ven_Creacion.title('Creación de mapa')
    fig = plt.figure(figsize=(834 / 90, 574 / 90), dpi=90)
    ax = fig.add_subplot(111)
    img = plt.imread("mapa.png")
    ax.imshow(img)
    canvas = FigureCanvasTkAgg(fig, ven_Creacion)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, ven_Creacion)
    toolbar.update()

    def onclick(event):
        global coordenadas, val_totalPuntos, lb_TotalPuntos, lb_PuntoPartida
        try:
            if(val_totalPuntos == 0 and respetarPrimero):
                plt.plot(event.xdata, event.ydata, "rX")
            else:
                plt.plot(event.xdata, event.ydata, "o")
            fig.canvas.draw()
            nuevoPunto = []
            nuevoPunto.append(round(event.xdata, 2))
            nuevoPunto.append(round(event.ydata, 2))
            coordenadas.append(nuevoPunto)
        except ValueError:
            msb.showerror(title='Error', message='La selección debe estar dentro del mapa')
        else:  # Si no hay excepción
            val_totalPuntos += 1
            lb_TotalPuntos.configure(text=str(val_totalPuntos))
            if (val_totalPuntos == 1 and respetarPrimero):
                coordX_proporcion = round((event.xdata * 40000 / 834), 2)
                coordY_proporcion = 40000 - round((event.ydata * 40000 / 574), 2)
                partida = '(' + str(coordX_proporcion) + ' , ' + str(round(coordY_proporcion)) + ')'
                lb_PuntoPartida.configure(text=partida)

    def formatoDePlot():
        ax.set_title("MAPA", fontsize='large', color='black', weight='bold')
        ax.set_xticks([208.5, 417, 625.5, 834])
        ax.set_xticklabels(['10000', '20000', '30000', '40000'])
        ax.set_yticks([430.5, 287, 143.5, 0])
        ax.set_yticklabels(['10000', '20000', '30000', '40000'])
        for tick in ax.xaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')
        for tick in ax.yaxis.get_ticklabels():
            tick.set_fontsize('small')
            tick.set_color('green')
            tick.set_weight('bold')

    def guardar():
        global coordenadas, val_totalPuntos
        continuarCarga = msb.askyesno(title='Continuar',
                                      message='Al guardar un archivo no se guarda el punto de inicio, ¿desea continuar?')
        if (continuarCarga):
            if (val_totalPuntos >= 2):
                file = asksaveasfile(mode='w',
                                     defaultextension=".txt")  # Abre el explorador para permitir elegir ubicación para guardar el archivo
                # y lo guarda en un txt
                if (file is not None):
                    for par in coordenadas:
                        for dato in par:
                            file.write(
                                str(dato) + ' ')  # Guarda valor por valor de una coordenada separándola por espacios
                        file.write('\n')  # Cambia de linea para ir a la siguiente coordenada (si hay)
                    file.close()  # Deja de escribir en el archivo
            else:
                msb.showerror(title='Error', message='Asegúrate de que la ruta cuente con al menos dos posiciones')

    def menuPrincipal():
        ven_Creacion.destroy()
        crearMenuPrincipal()

    def continuar():
        global val_totalPuntos
        if (val_totalPuntos >= 2):
            buscarCostoMinimo(ven_Creacion, respetarPrimero)
        else:
            msb.showerror(title='Error', message='Asegúrate de que la ruta cuente con al menos dos posiciones')

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
    fig.canvas.mpl_connect('button_press_event', onclick)
    formatoDePlot()
    plt.grid()
    fig.canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1, pady=10, padx=10)
    ven_Creacion.mainloop()

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
    crearMapa1 = tkinter.Button(ven_Principal, text='CREAR MAPA\ncon punto de partida', height=3, width=17)
    crearMapa1.configure(relief='groove', font='Helvetica 14 bold', bg="lightskyblue",
                        fg='black', activebackground='lightskyblue3', activeforeground='black',
                        command=lambda ventana=ven_Principal: crearMapa(ventana, True))
    crearMapa1.place(x=10, y=55)

    crearMapa2 = tkinter.Button(ven_Principal, text='CREAR MAPA\nsin punto de partida', height=3, width=17)
    crearMapa2.configure(relief='groove', font='Helvetica 14 bold', bg="greenyellow",
                         fg='black', activebackground='yellowgreen', activeforeground='black',
                         command=lambda ventana=ven_Principal: crearMapa(ventana, False))
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