from typing import Type
from django.db.models import Count, Q
from unfold.admin import mark_safe
from datetime import datetime, timedelta
from django.utils import timezone
from typing import NamedTuple


from causes.models import LearningResource, UserAction, Action, UserCampaign, UserCause, UserLearningResources, UserNewsArticle
from utils.models import TimeStampedMixin

def start_of_day(date: datetime) -> datetime:
    return timezone.make_aware(datetime(day=date.day, month=date.month, year=date.year))

def dashboard_callback(request, context):
    now = timezone.now()
    end_date = start_of_day(now) + timedelta(days=1)
    start_date = end_date - timedelta(days=7)

    kpis = [
        build_kpi(resource, now)
        for resource in
        [
            Resource(title="Actions completed", completion_class=UserAction),
            Resource(title="Learning resources completed", completion_class=UserLearningResources),
            Resource(title="News articles viewed", completion_class=UserNewsArticle),
            Resource(title="Campaigns completed", completion_class=UserCampaign),
            Resource(title="Causes joined", completion_class=UserCause),
        ]
    ]

    top_actions = Action.objects.all()\
        .annotate(
            completed_count=Count('completions', filter=Q(
                completions__created_at__gte=start_date,
                completions__created_at__lt=end_date,
            ))
        )\
        .order_by('completed_count')\
        .reverse()\
        .filter(completed_count__gt=0)\
        [:10]

    top_learning_resources = LearningResource.objects.all()\
        .annotate(
            completed_count=Count('completions', filter=Q(
                completions__created_at__gte=start_date,
                completions__created_at__lt=end_date,
            ))
        )\
        .order_by('completed_count')\
        .reverse()\
        .filter(completed_count__gt=0)\
        [:10]

    context.update(
        {
            "kpi": kpis,
            "top_actions": [
                {
                    "title": item.title,
                    "completed_count": item.completed_count,
                    "percentage_of_top": round((item.completed_count / top_actions[0].completed_count) * 100, 1),
                }
                for item in top_actions
            ],
            "top_learning_resources": [
                {
                    "title": item.title,
                    "completed_count": item.completed_count,
                    "percentage_of_top": round((item.completed_count / top_learning_resources[0].completed_count) * 100, 1),
                }
                for item in top_learning_resources
            ],
        }
    )

    return context

class Resource(NamedTuple):
    title: str
    completion_class: Type[TimeStampedMixin]

class CompletetionData(NamedTuple):
    num_completed_last_week: int
    percentage_increase_since_week_before: float | None

def build_kpi(resource: Resource, now: datetime):
    completion_data = compute_completion_data(resource.completion_class, now)

    return {
        "title": resource.title,
        "metric": completion_data.num_completed_last_week,
        "footer": build_footer(completion_data.percentage_increase_since_week_before),
    }

def compute_completion_data(model: Type[TimeStampedMixin], now: datetime) -> CompletetionData:
    # Very beginning of tomorrow
    end_date = now.date() + timedelta(days=1)
    start_date = end_date - timedelta(days=7)

    num_completed_last_week = model.objects.filter(
        created_at__gte=start_date,
        created_at__lt=end_date,
    ).count()
    num_completed_last_last_week = model.objects.filter(
        created_at__gte=start_date - timedelta(days=7),
        created_at__lt=start_date
    ).count()

    percentage_increase = ((num_completed_last_week - num_completed_last_last_week) / num_completed_last_last_week) * 100 if num_completed_last_last_week != 0 else None

    return CompletetionData(
        num_completed_last_week=num_completed_last_week,
        percentage_increase_since_week_before=percentage_increase,
    )

def get_footer_color(percentage_increase: float | None):
    if percentage_increase is None:
        return ''
    if percentage_increase > 0:
        return 'text-green-700 dark:text-green-400'
    return 'text-red-700 dark:text-red-400'

def get_footer_text_value(percentage_increase: float | None):
    if percentage_increase is None:
        return '-'
    if percentage_increase > 0:
        return f'+{percentage_increase}%'
    return f'{percentage_increase}%'

def build_footer(percentage_increase: float | None):
    text_color = get_footer_color(percentage_increase)
    text_value = get_footer_text_value(percentage_increase)

    return mark_safe(f'<strong class="{text_color} font-semibold">{text_value}</strong>&nbsp;progress from last week')
