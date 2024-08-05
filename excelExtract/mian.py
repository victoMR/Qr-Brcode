import re
import openpyxl
import warnings
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Suprimir advertencias
warnings.simplefilter("ignore")


def separar_texto(texto):
    pattern = re.compile(r',\s*(?![^(]*\))')
    partes = pattern.split(texto)
    partes_limpias = [parte.strip() for parte in partes if parte.strip()]

    # Mostrar el resultado en formato de lista
    for parte in partes_limpias:
        print(parte)

    return partes_limpias


def unir_texto():
    print("Introduce el texto separado por comas que quieres unir. Ingresa una línea vacía para finalizar:")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line.strip())

    texto_unido = ", ".join(lines)
    print("\nTexto unido con comas:")
    print(texto_unido)

    return texto_unido


def seleccionar_archivo():
    Tk().withdraw()  # Oculta la ventana principal de Tkinter
    file_path = askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsm;*.xlsx")])
    return file_path


def leer_desde_excel():
    file_path = seleccionar_archivo()
    if not file_path:
        print("No se seleccionó ningún archivo.")
        return ""

    sheet_name = input("Introduce el nombre de la hoja: ")
    cell_range = input("Introduce el rango de celdas (por ejemplo, C2:C27): ")

    workbook = openpyxl.load_workbook(file_path, data_only=True, keep_vba=True)
    sheet = workbook[sheet_name]

    cells = sheet[cell_range]
    texto = "\n".join([str(cell.value) for row in cells for cell in row if cell.value])

    return texto


def escribir_a_excel(data, filename="output.xlsx"):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    if isinstance(data, list):
        for idx, value in enumerate(data, start=1):
            sheet[f'A{idx}'] = value
    else:
        sheet['A1'] = data

    workbook.save(filename)
    print(f"Datos guardados en {filename}")


def main():
    print("Elige una opción:")
    print("1. Separar texto con comas")
    print("2. Unir texto con comas")
    print("3. Leer texto desde Excel y separar")
    print("4. Leer texto desde Excel y unir")
    opcion = input()

    if opcion == "1":
        texto = input("Introduce el texto a separar: ")
        partes = separar_texto(texto)
        escribir_a_excel(partes)
    elif opcion == "2":
        texto_unido = unir_texto()
        escribir_a_excel(texto_unido)
    elif opcion == "3":
        texto = leer_desde_excel()
        partes = separar_texto(texto)
        escribir_a_excel(partes)
    elif opcion == "4":
        texto = leer_desde_excel()
        texto_unido = ", ".join(texto.split("\n"))
        print("\nTexto unido con comas:")
        print(texto_unido)
        escribir_a_excel(texto_unido)
    else:
        print("Opción no válida. Por favor, elige 1, 2, 3 o 4.")


if __name__ == "__main__":
    main()
