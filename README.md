API de Banco de Dados para Notas Fiscais (invoices)
===================================================
Feito como desafio de desenvolvimento da Stone Pagamentos.

Esse sistema consiste de uma API REST, escrita em Python, utilizando o framework Flask.
O banco de dados utilizado foi SQLite3. Não foram usados ORMs.
A aplicação gerencia invoices, que são enviados e recebidos em formato JSON, e funciona sob autenticação por Token.

Modelo de invoice:
---------------------
```sql
Invoice
    ReferenceMonth : INTEGER
    ReferenceYear : INTEGER
    Document : VARCHAR(14)
    Description : VARCHAR(256)
    Amount : DECIMAL(16, 2)
    IsActive : TINYINT
    CreatedAt  : DATETIME
    DeactiveAt : DATETIME
```
Os campos `'IsActive'`, `'CreatedAt'`, `'DeactiveAt'` não serão fornecidos nem manipulados pelo usuário.

Endpoints de gestão de usuários:
-----------
+ **Adicionar novo usuário**:

   `'/nf/api/v1.0/users/register'`

   **Registra um novo usuário**. O novo usuário e senha devem ser fornecidos pelo método HTTP Basic Auth. Por meio do header `Authorization`, devem ser fornecidos o `username` e a `password` para o novo usuário. A senha é guardada em forma de *hash*. A função de *hash* utilizada gera um *salt* aleatório e retorna uma *hash*, que já inclui o *salt* também por ela gerado. Essa *hash* é guardada no banco de dados.
   
   Caso o usuário escolhido já exista, ou caso não sejam fornecidos usuário e senha, o sistema irá responder com `Error-400: Bad Request`.
   
+ **Gerar token**:

   `'/nf/api/v1.0/users/get_token'`

   É utilizado para **gerar uma *token***, quando o usuário já está cadastrado.
   
   Devem ser enviados `username` e `password`por meio do header `Authorization`, pelo método HTTP Basic Auth. Caso haja falha na autenticação, será retornado `Error 400: Bad Request`.
   
   A request retornará um JSON contendo a *token* desejada:
   ```JSON
   {
  "Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTc5MTI3MTAsImlhdCI6MTQ5NzkxMjQxMCwidXNlciI6ImR1cGxpY2FkbyJ9.uzns_876TsswcnW0Z-kkaha86chUxDa6YKr2rV2QSV8"
   }
   ```
   O tempo de validade da *token* pode ser ajustado no arquivo `app/config.py`.
   
+ **Excluir usuário**:

   `'/nf/api/v1.0/users/delete'`

   É utilizado para **deletar um usuário**. Basta que a autenticação por `username` e `password` seja completa da mesma forma dos passos anteriores, com HTTP Basic Auth, e caso esteja ativo no banco de dados, o usuário sofrerá uma deleção lógica.

Endpoints de gestão de invoices:
-----------------------------------------
+ **Autenticação**:

   **Para todos os endpoints dessa seção, os requests devem ser enviados com o header `Authorization`: `Bearer <token>`**. Se a *token* for validada, o servidor processará a request.
   
+ **POST**:

   `'/nf/api/v1.0/invoices'`, `POST`

   Usada para **adicionar novos invoices** à aplicação. No Body da request deve ser enviado um JSON com o seguinte formato:
   ```python
   {
	"ReferenceMonth": 11,
	"ReferenceYear": 2016,
    "Document": "Toyota Corolla",
    "Description":"Carro para uso dos executivos",
    "Amount": 75000.00
   }
   ```
   Caso a request tenha sido bem sucedido, será retornado um JSON com a representação completa do invoice:
   ```python
   {
  "invoice": {
    "Amount": 75000,
    "CreatedAt": "2017-06-19T20:39:18.956574",
    "DeactiveAt": null,
    "Description": "Carro para uso dos executivos",
    "Document": "Toyota Corolla",
    "IsActive": 1,
    "ReferenceMonth": 11,
    "ReferenceYear": 2016,
    "uri": "http://127.0.0.1:5000/nf/api/v1.0/invoices/36"
        }
     }
   ```
+ **GET ID**:

   `'/nf/api/v1.0/invoices/<id>'`, `GET`

   Usada para **acessar uma invoice específica pelo id**. Caso não seja encontrada, o servidor irá responder com `Error 404: Not Found`.
+ **UPDATE**:

   `'/nf/api/v1.0/invoices/<id>'`, `PUT`

   Usada para **atualizar as informações de alguma invoice já guardada**. O id corresponde ao id da invoice que será atualizada. Os campos passíveis de atualização são apenas os que podem ser controlados pelo usuário. No Body da request deve ser enviado um JSON contendo apenas os campos que devem ser atualizados, com seus respectivos novos valores.
+ **DELETE**:

   `'/nf/api/v1.0/invoices/<id>'`, `DELETE`

   Executa a **deleção lógica do invoice** correspondente ao id fornecido. O campo IsActive é atualizado para 0, e o campo DeactiveAt é preenchido com a data da deleção. O invoice excluído é retornado pelo servidor. Caso ele não seja encontrado, ocorrerá `ERROR 404: Not Found`.
+ **GET ALL**:

   `'/nf/api/v1.0/invoices'`, `GET`

   **Retorna todas as invoices**. Podem ser fornecidos, na URL, parametros de:
   + Paginação:
   
      `per-page=5`: 5 invoices serão exibidos em cada página.
      
      `page=2`: será exibida a segunda página de resultados.
   + Filtro:
   
      `referenceyear=2017`: filtra os resultados pelo campo ReferenceYear.
      
      `referencemonth=3`: filtra os resultados pelo campo ReferenceMonth.
      
      `document=Stone+Pagementos` filtra os resultados pelo campo Document.
   + Ordenação (sorting):
   
      `sort=referencemonth`: ordena de forma crescente, pelo campo ReferenceMonth.
      
      Para ordenar de forma decrescente, basta colocar um `-` na frente do parametro: `sort=-referencemonth`. Também é possível ordenar por `referenceyear` ou `document`, e por combinações entre eles:
   ```
   http://127.0.0.1:5000/nf/api/v1.0/invoices?sort=referenceyear,-referencemonth
   ```
   + Juntando os três:
   ```
   http://127.0.0.1:5000/nf/api/v1.0/invoices?per-page=2&page=1&referenceyear=2017&sort=-referencemonth
   ```
   
   
