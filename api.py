# api.py
from fastapi import APIRouter, Header, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from db.db import get_db
from modules.auth.oauth import get_current_user, credentials_exception
import base64
from typing import List

organization = APIRouter()

# Function to check permissions
async def check_permissions(db: AsyncSession, token: str, customization: bool):
    try:
        # JWT validation
        authorized = await get_current_user(db=db, token=token)
        
        if authorized["role"] == "system":
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise credentials_exception

@organization.post('/organization/update/name', tags=["ORGANIZATION"])
async def update_name(
    title: Name,
    token: str = Header(default=''),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check permissions
        if check_permissions(db, token, False):
            query = """
                UPDATE organization 
                SET name = :name
                WHERE id = :id_organization
                """

            await db.execute(query, {
                "name": title.name,
                "id_organization": title.organization_id
            })
            await db.commit()

            return JSONResponse({"message": "Name Updated", "success": True}, status_code=200)
        else:
            return JSONResponse({"message": "You do not have sufficient permissions to modify data", "success": False}, status_code=401)

    except Exception as e:
        print(e)
        return JSONResponse({"message": str(e), "success": False}, status_code=500)
@organization.post('/organization/update/id_organization', tags=["ORGANIZATION"])
async def update_id_organization(
    id_organization: int,
    token: str = Header(default=''),
    db: AsyncSession = Depends(get_db)
):
    try:
        # JWT validation
        authorized = await get_current_user(
            db=db,
            token=token
        )
        if not authorized:
            raise credentials_exception

        organization = await db.execute(
            """
            SELECT update 
            FROM organization 
            WHERE id = :id                       
        """, {
                "id": id_organization
            })
        organization = organization.one_or_none()
        update = False
        if organization:
            update = organization[0]

        if authorized["role"] == "system":

            # UPDATE DEFAULT LANGUAGE
            # Aquí va tu lógica para actualizar el idioma predeterminado

            return JSONResponse({"message": f"Default language updated to {Name.language}", "success": True}, status_code=200)
        else:
            raise HTTPException(status_code=401, detail="You do not have sufficient permissions to modify data")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Operation failed")

@organization.post('/organization/update/logo/{organization_id}', tags=["ORGANIZATION"])
async def update_logo_organization(
    organization_id: int,
    img: UploadFile,
    token: str = Header(default=''),
    db: AsyncSession = Depends(get_db)
):

    # JWT validation
    authorized = await get_current_user(
        db=db,
        token=token
    )
    if not authorized:
        raise credentials_exception

    try:

        organization = await db.execute(
            f"""
            SELECT update 
            FROM organization 
            WHERE id = {organization_id}                      
        """)
        organization = organization.one_or_none()

        update = False
        if organization:
            update = organization[0]

        if authorized["role"] == "system":
            # 1. PROCESS IMAGE
            # Read image data
            contents = await img.read()
            # Convert image data to base64
            base64_image = str(base64.b64encode(contents))[2:-1]

            # UPDATE ORGANIZATION IMAGE
            query = """
                UPDATE organization
                SET image = :image
                WHERE id = :id
                """
            await db.execute(query, {
                "image": base64_image,
                "id": organization_id
            })
            await db.commit()

            return JSONResponse({"message": "Logo updated", "success": True}, status_code=200)

        else:

            return JSONResponse({"message": "You do not have sufficient permissions to modify data", "success": False}, status_code=401)

    except Exception as e:

        print(e)
        return JSONResponse({"message": "Operation Failed", "success": False}, status_code=404)


async def enter_model_access_parameters(db, organization_id: int, model_db_username: str, model_db_password: str, model_db_host: str, model_db_port: int, model_db_name: str, token: str = Header(default='')):
    try:
        
        if check_permissions(db, token, False):
            # Aquí va la lógica para ingresar parámetros de acceso al modelo
            pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Operation failed")


async def enter_vectorized_db_access_parameters(db, organization_id: int, vectorized_db_username: str, vectorized_db_password: str, vectorized_db_host: str, vectorized_db_port: int, vectorized_db_name: str, token: str = Header(default='')):
    try:
        
        if check_permissions(db, token, False):
            # Aquí va la lógica para ingresar parámetros de acceso a la base de datos vectorizada
            pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Operation failed")


async def define_licensing_model(db, organization_id: int, max_users: int, token: str = Header(default='')):
    try:
        # Check permissions
        if check_permissions(db, token, False):
            # Aquí va la lógica para definir el modelo de licencias
            pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Operation failed")


async def define_storage_model(db, organization_id: int, max_gb_vectorize: int, token: str = Header(default='')):
    try:
        # Check permissions
        if check_permissions(db, token, False):
            # Aquí va la lógica para definir el modelo de almacenamiento
            pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Operation failed")
    
    
#### SYSTEM #####

async def add_new_organization(db, user_id: int, organization_name: str, addons: List[str], token: str = Header(default='')):
    try:
        # Check permissions
        if check_permissions(db, token, False):
            # Add a new organization record
            query = """
                INSERT INTO organization (name, creation_date, created_by, status)
                VALUES (:name, NOW(), :created_by, 'Active')
            """
            await db.execute(query, {"name": organization_name, "created_by": user_id})
            await db.commit()

            # Get the ID of the newly created organization
            organization_id = await get_organization_id_by_name(db, organization_name)

            # Add the AddOns to the new organization
            for addon in addons:
                available = "Yes" if addon == "TXT-GEN" else "No"
                query = """
                    INSERT INTO organization_addons (organization_id, addon_name, available)
                    VALUES (:organization_id, :addon_name, :available)
                """
                await db.execute(query, {"organization_id": organization_id, "addon_name": addon, "available": available})
                await db.commit()

            # Update internal audit attributes
            query = """
                UPDATE xOrganization
                SET CreationDate = NOW(), CreatedBy = :user_id, Status = 'Active'
                WHERE organization_id = :organization_id
            """
            await db.execute(query, {"user_id": user_id, "organization_id": organization_id})
            await db.commit()

            return JSONResponse({"message": f"Organization '{organization_name}' added successfully", "success": True}, status_code=200)
        else:
            raise HTTPException(status_code=401, detail="You do not have sufficient permissions to modify data")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Function to get the ID of the organization by its name
async def get_organization_id_by_name(db, organization_name: str) -> int:
    query = "SELECT id FROM organization WHERE name = :name"
    result = await db.fetch_one(query, {"name": organization_name})
    if result:
        return result["id"]
    else:
        raise HTTPException(status_code=404, detail=f"Organization with name '{organization_name}' not found")
