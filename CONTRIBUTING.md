# Guia de Contribuição - Marketing WhatsApp (Odoo 18)

Obrigado pelo seu interesse em contribuir com o projeto **Marketing WhatsApp**! Este projeto segue as diretrizes da **OCA (Odoo Community Association)** e as boas práticas de desenvolvimento do Odoo 18.

---

## 🚀 Como Contribuir

1. **Fork o repositório:** `https://github.com/Simplexo-br/marketing-whatsapp`
2. **Crie uma branch para sua feature:** `git checkout -b feature/minha-melhoria`
3. **Faça commit das alterações:** `git commit -m 'feat: adiciona suporte a template interativo'`
4. **Envie para a branch:** `git push origin feature/minha-melhoria`
5. **Abra um Pull Request (PR)** detalhando a alteração realizada.

---

## 📐 Padrões de Código

- **Python:** Conformidade com a PEP8 e padrões oficiais de nomenclatura de modelos do Odoo.
- **XML:** Indentação de 4 espaços, IDs descritivos e heranças modulares usando `xpath`.
- **Validação de Telefones:** Todo número de telefone deve ser sanitizado e validado via biblioteca `phonenumbers` antes de qualquer persistência ou disparo.
- **Segurança:** Toda nova tabela/modelo deve possuir suas respectivas regras no `ir.model.access.csv`.

---

## 📌 Links Importantes

- Repositório: [Simplexo-br/marketing-whatsapp](https://github.com/Simplexo-br/marketing-whatsapp)
- Gestão de Tarefas: [GitHub Projects #20](https://github.com/orgs/Simplexo-br/projects/20)
