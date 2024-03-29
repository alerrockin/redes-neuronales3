#----------------------------------------- Se importan las librerias ------------------------------------------
import cv2
import Informacion_manos as im
from playsound import playsound
import os
import  numpy as np
from keras_preprocessing.image import  load_img, img_to_array
from tensorflow.python.keras.models import load_model
import time
from threading import Timer

#-------------------------------------------------------------Funcion para decir el objeto en voz alta------------------------------------------------------------
def voz(nombre_objeto):
    return playsound(u"audio/" + nombre_objeto + ".mp3")

#------------------------------------------------------ Ubicacion del modelo y los pesos ---------------------------------------------------------
modelo = 'tmp\saved_model\SavedModel.h5'
peso = 'tmp\saved_model\SavedWeights.h5'

#----------------------------------------------------------- Se carga el modelo -----------------------------------------------------------------
cnn = load_model(modelo) #Se carga el modelo
cnn.load_weights(peso) #Se carga los pesos

#----------------------------------------------------------- Se carga los nombres de las carpetas -----------------------------------------------
direccion = modelo = 'Fotos\Entrenamiento'
dire_img = os.listdir(direccion)
print("Nombres: ", dire_img)

#------------------------------------------------------------------ Se declaran las variables ---------------------------------------------------
anchocam, altocam = 640, 480


#----------------------------------------------------------------------Lectura de la camara -----------------------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, anchocam) #Se define un ancho y un alto definido para siempre
cap.set(4, altocam)

#-------------------------------------------------------------Se declara el detector ------------------------------------------------------------
detector = im.detectormanos(maxManos=1, Confdeteccion=0.7) #Solo se utilizara una mano

while True:
    #------------------------Se va a encontrar los puntos de la mano ----------------------------------------------------------------
    ret, frame = cap.read()
    mano = detector.encontrarmanos(frame) #Encontramos las manos
    lista, bbox = detector.encontrarposicion(frame) #Se muestran las posiciones
    if len(lista) != 0:
        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[2]
        y2 = bbox[3]
        data = frame[y1:y2, x1:x2]
        try:
            obje = cv2.resize(data, (200, 200), interpolation = cv2.INTER_CUBIC) #Redimensiones de las fotos
        except Exception as e:
            print(e)
        x = img_to_array(obje) # Se convierte la imagen a una matriz
        x = np.expand_dims(x, axis=0) #Se agrega un nuevo eje
        vector = cnn.predict(x) # Sera un arreglo de 2 dimensiones, donde se va a poner 1 en la clase que crea correcta
        resultado = vector[0] # [1,0,0] [0,1,0] [0,0,1]
        respuesta = np.argmax(resultado) #Nos entrega el indice del valor más alto
        predicciones = list(range(0,3)) #aqui se cambia el rango dependiendo del numero de objetos entrenados
        if respuesta in predicciones:
            print(resultado)
            #cv2.rectangle(frame,(x1, y1), (x2, y2), (0,255, 0), 3)
            cv2.putText(frame, '{}'.format(dire_img[respuesta]), (x1, y1 - 5), 1, 2.5, (0, 255, 0), 3, cv2.LINE_AA)
            t = Timer(5, voz('{}'.format(dire_img[respuesta])))
            t.start()
        else:
            cv2.putText(frame, 'OBJETO DESCONOCIDO', (x1, y1 - 5), 1,1.3, (0, 0, 0), 1, cv2.LINE_AA)
            # voz("Objetodesconocido.mp3")
            t = Timer(5, voz("Objetodesconocido.mp3"))
            t.start()

    cv2.imshow("Clasificador", frame)
    k = cv2.waitKey(1)
    if k ==  27:
        break
cap.release()
cv2.destroyAllWindows()