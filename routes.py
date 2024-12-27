from flask_restful import Resource
from models import User
from functions import generate_preview, process_and_send_certificates
from flask import request, jsonify, Response
from models import db, User

#mainpage dashboard
class Dashboard(Resource):
    def get(x):
        return {"message": "Geek Room Dashboard!"}

#certificate Sender
class CertificateSender(Resource):
    def get(self):
        return {"message": "Certificate Sender"}
    def post(self):
        try:
            #Parsing the input
            data = request.json
            presentation_id = data.get('presentation_id')
            subject = data.get('subject')
            body = data.get('body')
            rows = data.get('rows')  # List of user data in JSON format

            if not (presentation_id and subject and body and rows):
                return {"error": "Missing required fields"}, 400
            
            # Process and send certificates for each user
            results = process_and_send_certificates(presentation_id, subject, body, rows)

            for row in rows:
                full_name = row.get("Full Name")
                email = row.get("Email")

                existing_user = User.query.filter_by(email=email).first()
                if not existing_user:
                    user = User(username=full_name, email=email)
                    db.session.add(user)


            # Committing all database changes
            db.session.commit()

            return {"message": "Certificates processed successfully", "results": results}, 200

        except Exception as e:
            #Rolling back in case of an error
            db.session.rollback()
            return {"error": str(e)}, 500

#preview shower
class CertificatePreview(Resource):
    def post(self):
        data = request.get_json()
        presentation_id = data.get('presentation_id')
        full_name = data.get('full_name')

        if not presentation_id or not full_name:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            # Generate the preview using the provided data
            image_data = generate_preview(presentation_id, full_name)
            if image_data:
                # Send the generated certificate as a JPG (image) file
                return Response(
                                image_data,
                                mimetype='image/jpeg',  # Adjust based on your image format
                                direct_passthrough=True
                                )
            else:
                return jsonify({"error": "Failed to generate certificate preview"}), 500
        except Exception as e:
            # Catch and log any unexpected errors
            return jsonify({"error": str(e)}), 500


#db connection checker
class Users(Resource):
    def get(self):
        try:
            users = User.query.all()
            # Format users as a list of dictionaries
            users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
            return {"users": users_list}, 200

        except Exception as e:
            return {"error": str(e)}, 500
