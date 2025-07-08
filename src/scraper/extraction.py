import re
import time
from selenium.webdriver.common.by import By


def extract_paragraphs_from_page(driver):
    # Aqui vamos começar a extração dos dados do PDF
    # Há muitas trocas de frames pois existe mais de um frame em cada PDF
    # E às vezes é necessário navegar entre as páginas para completar dados
    try:
        driver.switch_to.default_content()
        time.sleep(1)
        driver.switch_to.frame("bottomFrame")
        time.sleep(1)

        # Localiza onde está o conteúdo e ignora os primeiros 08 spans pois são cabeçalhos
        text_layer = driver.find_element(By.CLASS_NAME, "textLayer")
        spans = text_layer.find_elements(By.TAG_NAME, "span")[8:]

        paragraphs = []
        current = []

        # Olha cada span e começa a montar os parágrafos com base no início com "Processo""
        # Caso os spans iniciem com um parágrafo parcial ele salva assim mesmo para verificarmos depois
        for span in spans:
            text = span.text.strip()
            if text.startswith("Processo") and current:
                paragraphs.append(" ".join(current))
                current = []
            current.append(text)

        if current:
            paragraphs.append(" ".join(current))

        return paragraphs

    finally:
        driver.switch_to.default_content()


def fetch_previous_paragraph_if_incomplete(driver, paragraphs, relevant_paragraphs):
    # Aqui verificamos se o primeiro parágrafo está incompleto(Início do conteúdo no PDF anterior)
    first_paragraph = paragraphs[0]

    # Definimos como estar completo iniciar com "Processo" e terminar com o nome do advogado+OAB
    is_complete = (
        first_paragraph.strip().startswith("Processo")
        and re.search(r"\.\s*-\s*ADV:.*\(OAB\s*\d+/[A-Z]{2}\)", first_paragraph)
        is not None
    )

    # Se estiver completo não precisamos fazer nada
    if is_complete:
        return

    #  Como a lógica geral que eu fiz também pega os dados que estão incompletos "pra frente"
    #  Nós consideramos que se um dos termos estiver na página anterior eu não preciso tratar
    #  Esse parágrafo pois a outra função terá tratado. Mas se os dois termos estiverem aqui
    #  Significa que a parte inicial (Processo xxxx....) está no PDF anterior, então tratamos.
    if len(relevant_paragraphs) > 0:
        contains_rpv = "RPV" in first_paragraph
        contains_inss = "pagamento pelo INSS" in first_paragraph
        if not (contains_rpv and contains_inss):
            return

    # Voltamos para a página anterior para localizar o resto do conteúdo
    driver.switch_to.default_content()
    driver.switch_to.frame("mainFrame")
    driver.find_element(By.ID, "botaoVoltarPagina").click()
    time.sleep(2)

    driver.switch_to.default_content()
    driver.switch_to.frame("bottomFrame")

    text_layer = driver.find_element(By.CLASS_NAME, "textLayer")
    all_elements = text_layer.find_elements(By.XPATH, "./*")
    end_div = driver.find_element(By.CLASS_NAME, "endOfContent")
    end_index = all_elements.index(end_div)
    content_elements = all_elements[:end_index]
    content_spans = [el for el in content_elements if el.tag_name == "span"]

    texts = [s.text.strip() for s in content_spans]
    last_proc_index = max(
        (i for i, t in enumerate(texts) if t.startswith("Processo")), default=0
    )
    extra_text = " ".join(t for t in texts[last_proc_index:] if t)

    paragraphs[0] = f"{extra_text} {paragraphs[0]}"

    driver.switch_to.default_content()
    driver.switch_to.frame("mainFrame")
    driver.find_element(By.ID, "botaoAvancarPagina").click()
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame("bottomFrame")


def complete_last_paragraph_if_needed(driver, paragraphs):

    # Verifica se o último parágrafo está incompleto, e se for o caso,
    # acessa a próxima página do PDF e concatena os spans iniciais ao final do parágrafo.

    if not paragraphs:
        return

    last_paragraph = paragraphs[-1]

    # Se não tiver o termo RPV e nem o "pagamento pelo INSS" a função anterior vai tratar
    # se for um parágrafo que nos interessa e se não for já interrompemos logo
    if not ("RPV" in last_paragraph or "pagamento pelo INSS" in last_paragraph):
        return

    # Se já termina com a assinatura do advogado, não precisa completar
    if re.search(r"\.\s*-\s*ADV:.*\(OAB\s*\d+\/[A-Z]{2}\)", last_paragraph):
        return

    # Vai para próxima página
    driver.switch_to.default_content()
    driver.switch_to.frame("mainFrame")
    driver.find_element(By.ID, "botaoAvancarPagina").click()
    time.sleep(2)

    driver.switch_to.default_content()
    driver.switch_to.frame("bottomFrame")

    text_layer = driver.find_element(By.CLASS_NAME, "textLayer")
    spans = text_layer.find_elements(By.TAG_NAME, "span")[8:]

    process_indices = [
        i for i, span in enumerate(spans) if span.text.strip().startswith("Processo")
    ]
    end_index = process_indices[0] if process_indices else len(spans)

    continuation_text = " ".join(span.text.strip() for span in spans[:end_index])
    paragraphs[-1] += " " + continuation_text

    # Volta para página anterior
    driver.switch_to.default_content()
    driver.switch_to.frame("mainFrame")
    driver.find_element(By.ID, "botaoVoltarPagina").click()
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame("bottomFrame")


def extract_structured_data_from_paragraphs(paragraphs, publication_date):
    # Aqui apenas pegamos os parágrafos importantes e estruturamos os dados para envio
    results = []
    for text in paragraphs:
        if not ("RPV" in text and "pagamento pelo INSS" in text):
            continue

        numero_processo = extract_numero_processo(text)
        autores = extract_autores(text)
        advogados = extract_advogados(text)
        valor_bruto = extract_valor(text, "principal bruto/líquido")
        valor_juros = extract_valor(text, "juros moratórios")
        honorarios = extract_valor(text, "honorários advocatícios")

        results.append(
            {
                "text": text,
                "numero_processo": numero_processo,
                "autores": autores if autores else [],
                "advogados": advogados if advogados else [],
                "valor_principal_bruto_liquido": valor_bruto,
                "valor_juros_moratorios": valor_juros,
                "honorarios_advocaticios": honorarios,
                "data_publicacao": publication_date,
            }
        )
    return results


def extract_numero_processo(text):
    match = re.search(r"Processo\s+(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", text)
    return match.group(1) if match else None


def extract_autores(text):
    match = re.search(r"-\s*([^-]+?)\s*-\s*Vistos\.", text)
    autores = match.group(1) if match else None
    return [a.strip() for a in autores.split(",")] if autores else None


def extract_advogados(text):
    after_adv = re.search(r"ADV:\s*(.+)", text)
    if not after_adv:
        return None

    advogados_text = after_adv.group(1)

    matches = re.findall(r"[^,]+?\(OAB\s*\d+/\w+\)", advogados_text)
    return [m.strip() for m in matches] if matches else None


def extract_valor(text, label):
    pattern = rf"R\$\s*([\d\.,]+)\s*-\s*{label}"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None
