import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Camera, LucideAngularModule, Sparkles } from 'lucide-angular';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, LucideAngularModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'mercadona-chef';

  imageSrc: string | ArrayBuffer | null = null;

  readonly Camera = Camera;
  readonly Sparkles = Sparkles;

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

  onSubmit(): void {
    if (this.imageSrc) {
      const formData = new FormData();
      const blob = this.dataURLToBlob(this.imageSrc);
      formData.append('image', blob, 'uploaded-image.png');

      fetch('http://localhost:8000', {
        method: 'POST',
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to upload image');
          }
          return response.json();
        })
        .then((data) => {
          console.log('Image uploaded successfully:', data);
        })
        .catch((error) => {
          console.error('Error uploading image:', error);
        });
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
