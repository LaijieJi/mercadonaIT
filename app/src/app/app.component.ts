import { CommonModule } from '@angular/common';
import { Component, ChangeDetectorRef } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { type ServerResponse } from './models';
import {
  Camera,
  ChefHat,
  LoaderCircle,
  LucideAngularModule,
  Sparkles,
} from 'lucide-angular';

const exampleData: ServerResponse = {
  name: 'Espaguetis a la Carbonara',
  recipe: [
    'Hervir los espaguetis en agua con sal hasta que estén al dente.',
    'En una sartén aparte, cocinar la panceta hasta que esté crujiente.',
    'En un bol, batir los huevos con el queso.',
    'Escurrir los espaguetis y añadirlos a la sartén con la panceta.',
    'Retirar del fuego y mezclar rápidamente con la mezcla de huevo y queso.',
    'Servir inmediatamente con queso extra y pimienta.',
  ],
  ingredients: [
    {
      name: 'Espaguetis',
      img_url:
        'https://prod-mercadona.imgix.net/images/3a7e46ed332908a73cfe47f424e399c7.jpg?fit=crop&h=300&w=300',
      price: 1.25,
    },
    {
      name: 'Panceta',
      img_url: 'https://prod-mercadona.imgix.net/images/fb95cfe4590961e61d7a7fcf682cc64c.jpg?fit=crop&h=300&w=300',
      price: 3.25,
    },
    {
      name: 'Huevos',
      img_url:
        'https://prod-mercadona.imgix.net/images/24a770df80cb4ec523ffc6b606ab61c4.jpg?fit=crop&h=300&w=300',
      price: 1.5,
    },
    {
      name: 'Queso',
      img_url:
        'https://prod-mercadona.imgix.net/images/bfc088bcd08f0dc6e421323e51b5d9fa.jpg',
      price: 1.73,
    },
    {
      name: 'Aceite de Oliva',
      img_url:
        'https://prod-mercadona.imgix.net/images/bd24852bbc69423ae3bfed7fa04d4f28.jpg?fit=crop&h=300&w=300',
      price: 5.55,
    },
    {
      name: 'Pimienta Negra',
      img_url:
        'https://prod-mercadona.imgix.net/images/905e76fd8f59b3931ae5e2c586c4a9f5.jpg?fit=crop&h=300&w=300',
      price: 1.3,
    },
    {
      name: 'Sal',
      img_url:
        'https://prod-mercadona.imgix.net/images/5097b3d7450edab7c2d9586299f5f3b9.jpg?fit=crop&h=300&w=300',
      price: 0.4,
    },
  ],
};

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, LucideAngularModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'mercadona-chef';

  imageSrc: string | ArrayBuffer | null = null;
  isSubmitting = false;
  response: ServerResponse | null = null;
  loadingStatus: string = '';
  errorMessage: string | null = null;

  readonly Camera = Camera;
  readonly Sparkles = Sparkles;
  readonly ChefHat = ChefHat;
  readonly LoaderCircle = LoaderCircle;

  constructor(private cdr: ChangeDetectorRef) {}

  get totalPrice(): number {
    if (!this.response?.ingredients) return 0;
    return this.response.ingredients.reduce((sum, ing) => sum + (ing.price || 0), 0);
  }

  adjustTextareaHeight(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageSrc = e.target?.result || null;
      };
      reader.readAsDataURL(input.files[0]);
    }
  }
  async onSubmit(): Promise<void> {
    if (this.imageSrc) {
      this.isSubmitting = true;
      this.errorMessage = null;
      this.loadingStatus = 'Clasificando imagen...';

      const formData = new FormData();
      const blob = this.dataURLToBlob(this.imageSrc);
      formData.append('image', blob, 'uploaded-image.png');

      try {
        this.loadingStatus = 'Generando receta...';
        const response = await fetch('http://localhost:8000', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload image');
        }

        this.loadingStatus = 'Buscando productos...';
        const data = await response.json();
        console.log('Image uploaded successfully:');
        console.log('Name:', data.name);
        console.log('Recipe:', data.recipe);
        console.log('Ingredients:', data.ingredients);

        this.response = data;
        this.errorMessage = null;
        this.cdr.detectChanges();
      } catch (error: any) {
        console.error('Error uploading image:', error);
        console.error('Error name:', error?.name);
        console.error('Error message:', error?.message);
        console.error('Error stack:', error?.stack);
        this.errorMessage = `Error: ${error?.message || 'No se pudo analizar la imagen'}. Mostrando ejemplo.`;
        this.response = exampleData;
        this.cdr.detectChanges();
      } finally {
        this.isSubmitting = false;
        this.loadingStatus = '';
        this.cdr.detectChanges();
      }
    } else {
      console.error('No image selected to upload.');
    }
  }

  private dataURLToBlob(dataURL: string | ArrayBuffer): Blob {
    const byteString = atob((dataURL as string).split(',')[1]);
    const mimeString = (dataURL as string)
      .split(',')[0]
      .split(':')[1]
      .split(';')[0];
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uint8Array = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
      uint8Array[i] = byteString.charCodeAt(i);
    }

    return new Blob([arrayBuffer], { type: mimeString });
  }
}
