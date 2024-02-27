import streamlit as st


# Título y descripción
st.title("Bienvenido al Visualizador de Futuros de Commodities")
st.divider()  # 👈 Draws a horizontal rule
st.write("Este proyecto te permite visualizar información sobre los precios de los futuros de distintos commodities y calcular estrategias de arbitraje.")
st.divider()  # 👈 Draws a horizontal rule
# Breve descripción del proyecto
st.write("""
El objetivo de estre proyecto es proporcionar información actualizada sobre los precios de los futuros de commodities y ayudar a explorar estrategias de arbitraje entre futuros combinando Commodities / Mercados / Vencimientos.
""")

st.divider()  # 👈 Draws a horizontal rule
st.write("""
Se tiene información de los mercaoos CME y ROS.
""")

st.divider()  # 👈 Draws a horizontal rule
st.write("""
Es importante tener en cuenta que existe un archivo llamado "retenciones.csv" que es dónde hay que colocar las retenciones que aplican a cada commodity y durante qué período aplican.
""")

st.divider()  # 👈 Draws a horizontal rule
st.write("""
Toda la información se actualiza de la API de MATBA ROFEX: [API - reMarkets](https://remarkets.primary.ventures/)
""")

# Contacto o enlaces relevantes (puedes agregar más)
st.sidebar.write("Contacto:")

# Enlaces a los perfiles de WhatsApp y LinkedIn (reemplaza con tus propios enlaces)
gmail_link = "octa.bidegain@gmail.com"
whatsapp_link = "https://wa.me/542262339461"
linkedin_link = "https://www.linkedin.com/in/obidegain/"

# Íconos de contacto
st.sidebar.write("""
    <a href="{}" target="_blank" style="text-decoration:none; color:#D14836">
        <i class="fas fa-envelope"></i> Gmail
    </a>
""".format(gmail_link), unsafe_allow_html=True)
st.sidebar.write("""
    <a href="{}" target="_blank" style="text-decoration:none; color:#0077B5">
        <i class="fab fa-linkedin"></i> LinkedIn
    </a>
""".format(linkedin_link), unsafe_allow_html=True)

st.sidebar.write("""
    <a href="{}" target="_blank" style="text-decoration:none; color:#25D366">
        <i class="fab fa-whatsapp"></i> WhatsApp
    </a>
""".format(whatsapp_link), unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">', unsafe_allow_html=True)

# Pie de página
st.sidebar.write("© 2023 Octavio Bidegain")
