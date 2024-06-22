import logging
from datetime import datetime, timedelta

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLimiterMiddleware(MiddlewareMixin):
    request_count_limit = 5
    # Adjust this value as needed
    time_frame = timedelta(minutes=5)  # Adjust this value as needed

    ip_request_count = {}

    def process_request(self, request):
        # Log the location (IP address) of the request
        ip_address = self.get_client_ip(request)
        logger.info(f"Received request from IP: {ip_address}")
        print(self.ip_request_count)


        # Increment the request count for the IP address
        # Check if the 'source' header is present in the request
        source_header = request.headers.get('source',None)
        # Check if IP is blocked
        if self.is_ip_blocked(ip_address):
            if source_header != None:
                logger.warning(f"IP address {ip_address} is blocked due to high request count.")
                print("Blocked")
                return HttpResponseForbidden("Your IP address has been blocked due to high request count.")

        if source_header:
            self.increment_request_count(ip_address)
            # Set values on the request object to pass to the view
            request.META['client_ip'] = ip_address
            request.META['request_count'] = self.ip_request_count[ip_address][1]
            request.META['source'] = source_header
        else:
            request.META['client_ip'] = "Dashboard Self"
            request.META['request_count'] = "-"
            request.META['source'] = "Admin"
            request.META['all'] = self.ip_request_count

    def increment_request_count(self, ip_address):
        current_time = datetime.now()
        if ip_address in self.ip_request_count:
            last_request_time, count = self.ip_request_count[ip_address]
            if current_time - last_request_time > self.time_frame:
                self.ip_request_count[ip_address] = (current_time, 1)
            else:
                self.ip_request_count[ip_address] = (last_request_time, count + 1)
        else:
            self.ip_request_count[ip_address] = (current_time, 1)

    def is_ip_blocked(self, ip_address):
        current_time = datetime.now()
        if ip_address in self.ip_request_count:
            last_request_time, count = self.ip_request_count[ip_address]
            if current_time - last_request_time <= self.time_frame and count > self.request_count_limit:
                return True
        return False

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
