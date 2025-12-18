import os

# Define the base directory for templates
base_template_dir = "app/templates"

# Define the form templates to be created
form_templates = {
    "clients": {
        "form_name": "ClientForm",
        "fields": [
            ("Tipo de Cliente", "{{ form.tipo.label }} {{ form.tipo(class='radio') }}"),
            ("Nome / Razão Social", "{{ form.nome_razao.label }} {{ form.nome_razao(class='input input-bordered') }}"),
            ("Endereço", "{{ form.endereco.label }} {{ form.endereco(class='textarea textarea-bordered') }}"),
            ("Nacionalidade", "{{ form.nacionalidade.label }} {{ form.nacionalidade(class='input input-bordered') }}"),
            ("Estado Civil", "{{ form.estado_civil.label }} {{ form.estado_civil(class='input input-bordered') }}"),
            ("Profissão", "{{ form.profissao.label }} {{ form.profissao(class='input input-bordered') }}"),
            ("RG", "{{ form.rg.label }} {{ form.rg(class='input input-bordered') }}"),
            ("Órgão Emissor do RG", "{{ form.orgao_emissor_rg.label }} {{ form.orgao_emissor_rg(class='input input-bordered') }}"),
            ("CPF", "{{ form.cpf.label }} {{ form.cpf(class='input input-bordered') }}"),
            ("E-mail", "{{ form.email.label }} {{ form.email(class='input input-bordered') }}"),
            ("Telefone", "{{ form.telefone.label }} {{ form.telefone(class='input input-bordered') }}"),
            ("CNPJ/CPF", "{{ form.cnpj.label }} {{ form.cnpj(class='input input-bordered') }}"),
            ("Representante Legal", "{{ form.representante_nome.label }} {{ form.representante_nome(class='input input-bordered') }}"),
            ("E-mail do Representante", "{{ form.representante_email.label }} {{ form.representante_email(class='input input-bordered') }}"),
            ("Telefone do Representante", "{{ form.representante_telefone.label }} {{ form.representante_telefone(class='input input-bordered') }}"),
            ("Função/Cargo do Representante", "{{ form.representante_funcao.label }} {{ form.representante_funcao(class='input input-bordered') }}"),
        ]
    },
    "dealers": {
        "form_name": "DealerForm",
        "fields": [
            ("Razão Social", "{{ form.razao_social.label }} {{ form.razao_social(class='input input-bordered') }}"),
            ("Endereço", "{{ form.endereco.label }} {{ form.endereco(class='textarea textarea-bordered') }}"),
            ("CNPJ", "{{ form.cnpj.label }} {{ form.cnpj(class='input input-bordered') }}"),
            ("Representante Legal", "{{ form.representante_nome.label }} {{ form.representante_nome(class='input input-bordered') }}"),
            ("E-mail do Representante", "{{ form.representante_email.label }} {{ form.representante_email(class='input input-bordered') }}"),
            ("Telefone do Representante", "{{ form.representante_telefone.label }} {{ form.representante_telefone(class='input input-bordered') }}"),
            ("Função/Cargo do Representante", "{{ form.representante_funcao.label }} {{ form.representante_funcao(class='input input-bordered') }}"),
        ]
    },
    "inventory": {
        "form_name": "EquipmentForm",
        "fields": [
            ("Nome do Equipamento (Item)", "{{ form.name.label }} {{ form.name(class='input input-bordered') }}"),
            ("PN (Part Number)", "{{ form.pn.label }} {{ form.pn(class='input input-bordered') }}"),
            ("Model Number", "{{ form.model_number.label }} {{ form.model_number(class='input input-bordered') }}"),
            ("Nº de Série", "{{ form.serial_number.label }} {{ form.serial_number(class='input input-bordered') }}"),
            ("Machine Installed", "{{ form.machine_installed.label }} {{ form.machine_installed(class='input input-bordered') }}"),
            ("Imagem de Referência", "{{ form.image_ref.label }} {{ form.image_ref(class='input input-bordered') }}"),
            ("Patrimônio/Código", "{{ form.asset_tag.label }} {{ form.asset_tag(class='input input-bordered') }}"),
            ("Categoria", "{{ form.category.label }} {{ form.category(class='input input-bordered') }}"),
            ("Marca", "{{ form.brand.label }} {{ form.brand(class='input input-bordered') }}"),
            ("Owner", "{{ form.owner_id.label }} {{ form.owner_id(class='select select-bordered') }}"),
            ("Current Responsible", "{{ form.current_responsible_id.label }} {{ form.current_responsible_id(class='select select-bordered') }}"),
            ("Location (Cliente)", "{{ form.location_id.label }} {{ form.location_id(class='select select-bordered') }}"),
            ("Projeto", "{{ form.project_id.label }} {{ form.project_id(class='select select-bordered') }}"),
            ("Status", "{{ form.status_id.label }} {{ form.status_id(class='select select-bordered') }}"),
            ("Observações", "{{ form.notes.label }} {{ form.notes(class='textarea textarea-bordered') }}"),
        ]
    }
}

# Create the HTML content for each form
for section, config in form_templates.items():
    section_dir = os.path.join(base_template_dir, section)
    os.makedirs(section_dir, exist_ok=True)
    file_path = os.path.join(section_dir, "form.html")
    print(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{% extends 'base.html' %}\n")
        f.write("{% block content %}\n")
        f.write(f"<h2>Formulário - {section.capitalize()}</h2>\n")
        f.write("<form method=\"POST\">\n")
        f.write("{{ form.hidden_tag() }}\n")
        for label, field_html in config["fields"]:
            f.write("<div class=\"form-group\" style=\"margin-bottom: 1em;\">\n")
            f.write(f"  <label>{label}</label><br>\n")
            f.write(f"  {field_html}\n")
            f.write("</div>\n")
        f.write("<div>\n")
        f.write("  {{ form.submit(class='btn btn-primary') }}\n")
        f.write("</div>\n")
        f.write("</form>\n")
        f.write("{% endblock %}\n")

