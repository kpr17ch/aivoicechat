from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from twilio.twiml.voice_response import VoiceResponse, Connect

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content="<h1>Twilio Media Stream Server is running!</h1>")


@router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")
