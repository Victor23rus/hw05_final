from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'Привет, я Виктор! Автор этого проекта.'
        context['author_text'] = (
            'Я начинающий программист. Вот ссылка на мой Github'
            ' https://github.com/Victor23rus'
            '. Я умею еще мало в программировании но я постоянно учусь и узнаю'
            ' новые возможности для себя. В программировании привлек тот факт,'
            ' что можно работать из любой точки мира. Это огромный плюс'
            ' для путешественников. Во время создаия этого проекта'
            ' мне помогала аквариумная рыбка Дори:)')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'На чем основывается проект?'
        context['tech_text'] = (
            'В данном проекте были пременены стандартные для Python методы'
            ' програмирования с применением классов, функций и декораторов.'
            ' Использовался фреймворк Django, он отвечает за оболочку сайта.'
            ' Применена технология Bootstrap отвечающая за красоту сайта.')
        return context
