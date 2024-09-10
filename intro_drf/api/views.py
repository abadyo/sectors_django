from django.shortcuts import render
from .serializer import *
from .models import Institutions, Metadata, Reports
from rest_framework.generics import ListAPIView
from django.core.cache import cache
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class InstitutionsView(ListAPIView):
    queryset = Institutions.objects.all()
    serializer_class = InstituionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        # print(f"queryset: {queryset}")
        institution_name = self.request.query_params.get("name", None)
        if institution_name:
            queryset = queryset.filter(
                Q(top_sellers__contains=[{"name": institution_name}])
                | Q(top_buyers__contains=[{"name": institution_name}])
            )
        return queryset

    def list(self, request):
        x = request.GET.get("name", "")

        cache_key = f"get-institution-{'all' if x == '' else x} "  # Define a unique cache key for this data
        print(f"cache_key: {cache_key}")  # Log the cache key (for debugging purposes)
        result = cache.get(
            cache_key
        )  # Attempt to retrieve cached data using the cache key

        if not result:  # If no cache is found
            print("Hitting DB")  # Log to indicate a database query is being made
            result = self.get_queryset()  # Query the database for the data

            if not result:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                )

            cache.set(cache_key, result, 60)  # Cache the result for 60 seconds
        else:
            print("Cache retrieved!")  # Log to indicate that cached data was retrieved

        # Serialize the result to prepare it for the response
        result = self.serializer_class(result, many=True)
        # print(result.data)  # Log the serialized data (for debugging purposes)

        return Response(
            result.data, status=status.HTTP_200_OK
        )  # Return the serialized data as a response


class MetadataView(ListAPIView):
    queryset = Metadata.objects.all()
    serializer_class = MetadataSerializer

    # get parameter from url
    def get_queryset(self):
        queryset = super().get_queryset()
        sector = self.request.query_params.get("sector", None)
        sub_sector = self.request.query_params.get("sub_sector", None)

        if sector and sub_sector:
            queryset = queryset.filter(
                Q(sector__icontains=sector) & Q(sub_sector__icontains=sub_sector)
            )
        elif sector:
            queryset = queryset.filter(Q(sector__icontains=sector))
        elif sub_sector:
            queryset = queryset.filter(Q(sub_sector__icontains=sub_sector))
        return queryset

    def list(self, request):
        x = request.GET.get("sector", "")
        y = request.GET.get("sub_sector", "")

        cache_key = f"get-metadata-{'' if x == '' else x}-{'' if y == '' else y}"
        result = cache.get(cache_key)
        # print(f"cache_key: {cache_key}")
        # print(f"result: {result}")

        if not result:
            print("Hitting DB")
            result = self.get_queryset()

            if not result:
                return Response(status=status.HTTP_404_NOT_FOUND)

            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        # print(result.data)  # Log the serialized data (for debugging purposes)

        return Response(result.data, status=status.HTTP_200_OK)


# TODO add cache
class ReportsView(ListAPIView):
    queryset = Reports.objects.all()
    serializer_class = ReportsSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sub_sector = self.request.query_params.get("sub_sector", None)
        total_companies = self.request.query_params.get("compy", None)
        method = self.request.query_params.get("method", None)
        top = self.request.query_params.get("top", None)

        if top:
            queryset = queryset.order_by("-total_market_cap")[: int(top)]
        if sub_sector:
            queryset = queryset.filter(sub_sector__icontains=sub_sector)
        elif total_companies and method:
            if method == "gte":
                queryset = queryset.filter(total_companies__gte=total_companies)
            elif method == "lte":
                queryset = queryset.filter(total_companies__lte=total_companies)
        return queryset

    def list(self, request):
        x = request.GET.get("sub_sector", "")
        total_companies = request.GET.get("compy", "")
        method = request.GET.get("method", "")
        top = request.GET.get("top", "")

        cache_key = f"get-reports-{'all' if x == '' else x}-{'none' if total_companies == '' else total_companies}-{'none' if method == '' else method}-{'none' if top == '' else top}"
        result = cache.get(cache_key)

        print(f"cache_key: {cache_key}")
        # print(f"result: {result}")

        if not result:
            print("Hitting DB")
            result = self.get_queryset()

            if not result:
                return Response(status=status.HTTP_404_NOT_FOUND)

            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        # print(result.data)  # Log the serialized data (for debugging purposes)

        return Response(result.data, status=status.HTTP_200_OK)


class IDXView(ListAPIView):
    queryset = IDXSummary.objects.all()
    serializer_class = IDXSummarySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        ticker = self.request.query_params.get("ticker", None)

        if ticker:
            queryset = queryset.filter(ticker__icontains=ticker)
        return queryset

    def list(self, request):
        x = request.GET.get("ticker", "")

        cache_key = f"get-idx-summary-{'all' if x == '' else x}"
        result = cache.get(cache_key)

        print(f"cache_key: {cache_key}")
        # print(f"result: {result}")

        if not result:
            print("Hitting DB")
            result = self.get_queryset()

            if not result:
                return Response(status=status.HTTP_404_NOT_FOUND)

            cache.set(cache_key, result, 60)
        else:
            print("Cache retrieved!")
        result = self.serializer_class(result, many=True)
        # print(result.data)  # Log the serialized data (for debugging purposes)

        return Response(result.data, status=status.HTTP_200_OK)
