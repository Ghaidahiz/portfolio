from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import re
import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv
import markdown


load_dotenv('api.env')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class RecipeRequest(BaseModel):
    ingredients: str
    
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("createRecipe.html", {"request": request})

@app.post("/createrecipe")
def generate_recipe(ingList: str = Form(...)):
    try:
        recRequest = RecipeRequest(ingredients=ingList)
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=20000,
            temperature=0.7,
            system="أنت طاهٍ محترف متخصص في إعداد وصفات متقنة. مهمتك هي تحويل قائمة المكونات التي يقدمها المستخدم إلى وصفة شهية ومفصلة, واكتبها بصيغة markdown، اذا اعطاك المستخدم طلب لا يتعلق بمكونات الطعام اطلب منه ادخال مكونات صحيحة مع الالتزام بما يلي (دائما استخدم هذه الصيغة):  إضافة عنوان جذاب للوصفة تحت العنوان \"اسم الوصفة:\" عرض قائمة المكونات بوضوح تحت العنوان \"المكونات:\"، دون إضافة أي مكونات خارج القائمة المقدمة من المستخدم، باستثناء البهارات مثل الملح والفلفل الأسود وغيرها. تقديم خطوات التحضير بشكل دقيق وواضح تحت العنوان \"طريقة التحضير:\"، بحيث يكون لكل خطوة ترتيب منطقي لتحقيق أفضل نتيجة. التعليمات: لا تضف أي مكونات غير مذكورة في قائمة المستخدم، إلا البهارات مثل الملح والفلفل الأسود وما شابه. قم بتنظيم المكونات وفقًا لاستخدامها في الوصفة. اجعل خطوات الطهي واضحة ومنسقة لضمان سهولة التنفيذ. إذا لم يحدد المستخدم كميات المكونات، اتركها كما هي أو قدم اقتراحات بشكل اختياري. لا تضف نصائح إضافية أو اقتراحات لمكونات أخرى غير مذكورة. مثال إدخال من المستخدم: \"دجاج، ثوم، طماطم، بصل، زيت زيتون، معكرونة\"  مثال إخراج متوقع:  اسم الوصفة: معكرونة الدجاج بالطماطم والثوم  المكونات:  دجاج ثوم طماطم بصل زيت زيتون معكرونة ملح فلفل أسود طريقة التحضير:  اسلق المعكرونة في ماء مغلي ومملح حتى تنضج، ثم صفيها واتركها جانبًا. سخن زيت الزيتون في مقلاة، ثم أضف البصل والثوم وقلّبهما حتى يذبلا. أضف الدجاج المقطع واطهه حتى يكتسب لونًا ذهبيًا. أضف الطماطم المفرومة، الملح، والفلفل الأسود، واترك الخليط يطهى حتى تتجانس النكهات. أضف المعكرونة المسلوقة وقلّبها مع باقي المكونات لمدة دقيقتين. قدّم المعكرونة ساخنة واستمتع بها. ",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": recRequest.ingredients
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "اسم الوصفة:"},
                        {"type": "text", "text": "المكونات:"},
                        {"type": "text", "text": "طريقة التحضير:"}
            ]
        }])
        full_text = " ".join(block.text for block in message.content)
        full_text = full_text.strip()
        html_content = markdown.markdown(full_text, extensions=['fenced_code', 'tables', 'nl2br'])
        print(full_text)  
        print(html_content) 
        return templates.TemplateResponse("result.html", {
            "request": recRequest.model_dump(),  
            "html_content": html_content 
        })
    except Exception as e:
        raise HTTPException(status_code=550, detail=f"Error generating recipe: {str(e)}")
    # print(full_text)
    # # تقسيم النص إلى أقسام
    # sections = re.split(r"اسم الوصفة:|المكونات:|طريقة التحضير:", full_text)
    # if len(sections) < 4:
    #     raise ValueError("الاستجابة ليست بالصيغة المتوقعة.")

    # title = sections[1].strip()
    # ingredients = sections[2].strip()
    # steps = sections[3].strip()

    # print("اسم الوصفة:", title)
    # print("المكونات:", ingredients)
    # print("طريقة التحضير:", steps)

    # return templates.TemplateResponse("result.html", {
    #     "request": recRequest.model_dump(),
    #     "title": title,
    #     "ingredients": ingredients,
    #     "steps": steps})
